from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app import db
from app.models.models import Item, InboundRecord, OperationLog
from app.routes.auth import role_required
from app.utils.helpers import generate_record_no, check_inventory_alert, resolve_inventory_alerts
from datetime import datetime
import pandas as pd
import io

inbound_bp = Blueprint('inbound', __name__)

INBOUND_TYPES = {
    'purchase': '采购入库',
    'return': '退货入库',
    'transfer': '调拨入库',
    'other': '其他入库'
}

ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

FIELD_MAPPING = {
    '物品编码': 'item_code',
    '编码': 'item_code',
    '物品名称': 'name',
    '名称': 'name',
    '数量': 'quantity',
    '入库数量': 'quantity',
    '单价': 'unit_price',
    '来源': 'source',
    '供应商': 'supplier',
    '经手人': 'handler',
    '备注': 'remark',
    '说明': 'remark'
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def auto_map_columns(columns):
    mapped = {}
    for col in columns:
        col_str = str(col).strip()
        for key, value in FIELD_MAPPING.items():
            if key in col_str or col_str in key:
                mapped[col] = value
                break
        if col not in mapped:
            mapped[col] = col_str.lower().replace(' ', '_')
    return mapped

@inbound_bp.route('', methods=['GET'])
@jwt_required()
def get_inbound_records():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    inbound_type = request.args.get('inbound_type', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    query = InboundRecord.query
    
    if search:
        query = query.filter(
            (InboundRecord.record_no.contains(search)) |
            (InboundRecord.item_code.contains(search)) |
            (InboundRecord.item_name.contains(search))
        )
    
    if inbound_type:
        query = query.filter(InboundRecord.inbound_type == inbound_type)
    
    if start_date:
        query = query.filter(InboundRecord.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
    
    if end_date:
        query = query.filter(InboundRecord.created_at <= datetime.strptime(end_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S'))
    
    pagination = query.order_by(InboundRecord.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'records': [record.to_dict() for record in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@inbound_bp.route('/<int:record_id>', methods=['GET'])
@jwt_required()
def get_inbound_record(record_id):
    record = InboundRecord.query.get(record_id)
    
    if not record:
        return jsonify({'message': '记录不存在'}), 404
    
    return jsonify(record.to_dict()), 200

@inbound_bp.route('', methods=['POST'])
@role_required('admin', 'operator')
def create_inbound_record():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    item_id = data.get('item_id')
    item = Item.query.get(item_id)
    
    if not item:
        return jsonify({'message': '物品不存在'}), 404
    
    quantity = float(data.get('quantity', 0))
    unit_price = float(data.get('unit_price', item.unit_price))
    total_price = quantity * unit_price
    
    record_no = generate_record_no('RK')
    
    record = InboundRecord(
        record_no=record_no,
        item_id=item.id,
        item_code=item.item_code,
        item_name=item.name,
        inbound_type=data.get('inbound_type', 'purchase'),
        quantity=quantity,
        unit_price=unit_price,
        total_price=total_price,
        source=data.get('source'),
        supplier=data.get('supplier'),
        handler=data.get('handler'),
        operator_id=current_user_id,
        remark=data.get('remark')
    )
    
    db.session.add(record)
    
    item.quantity += quantity
    item.unit_price = unit_price
    
    log = OperationLog(
        user_id=current_user_id,
        operation='入库',
        module='入库管理',
        description=f'入库单号: {record_no}, 物品: {item.name}, 数量: {quantity}'
    )
    db.session.add(log)
    
    db.session.commit()
    
    check_inventory_alert(item)
    resolve_inventory_alerts(item)
    
    return jsonify({
        'message': '入库成功',
        'record': record.to_dict()
    }), 201

@inbound_bp.route('/types', methods=['GET'])
@jwt_required()
def get_inbound_types():
    return jsonify(INBOUND_TYPES), 200

@inbound_bp.route('/import', methods=['POST'])
@role_required('admin', 'operator')
def batch_import_inbound():
    current_user_id = get_jwt_identity()
    
    if 'file' not in request.files:
        return jsonify({'message': '没有上传文件'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'message': '没有选择文件'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'message': '不支持的文件格式，请上传Excel或CSV文件'}), 400
    
    try:
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        
        if file_ext == 'csv':
            df = pd.read_csv(file, encoding='utf-8-sig')
        else:
            df = pd.read_excel(file)
        
        if df.empty:
            return jsonify({'message': '文件内容为空'}), 400
        
        df.columns = df.columns.str.strip()
        column_mapping = auto_map_columns(df.columns)
        
        success_count = 0
        error_list = []
        new_item_count = 0
        
        for index, row in df.iterrows():
            row_num = index + 2
            
            try:
                item_data = {}
                for col, field in column_mapping.items():
                    if col in df.columns and pd.notna(row[col]):
                        item_data[field] = row[col]
                
                item_code = item_data.get('item_code', '')
                item_name = item_data.get('name', '')
                
                if not item_code and not item_name:
                    error_list.append(f'第{row_num}行: 缺少物品编码或物品名称')
                    continue
                
                quantity = float(item_data.get('quantity', 0))
                if quantity <= 0:
                    error_list.append(f'第{row_num}行: 数量必须大于0')
                    continue
                
                unit_price = float(item_data.get('unit_price', 0))
                
                if item_code:
                    item = Item.query.filter_by(item_code=str(item_code)).first()
                else:
                    item = Item.query.filter_by(name=str(item_name)).first()
                
                if not item:
                    if item_code:
                        item = Item(
                            item_code=str(item_code),
                            name=str(item_name) if item_name else str(item_code),
                            unit='个',
                            unit_price=unit_price,
                            quantity=0
                        )
                        db.session.add(item)
                        db.session.flush()
                        new_item_count += 1
                    else:
                        error_list.append(f'第{row_num}行: 物品不存在且无编码无法创建')
                        continue
                
                record_no = generate_record_no('RK')
                
                record = InboundRecord(
                    record_no=record_no,
                    item_id=item.id,
                    item_code=item.item_code,
                    item_name=item.name,
                    inbound_type='purchase',
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=quantity * unit_price,
                    source=str(item_data.get('source', '')) if item_data.get('source') else None,
                    supplier=str(item_data.get('supplier', '')) if item_data.get('supplier') else None,
                    handler=str(item_data.get('handler', '')) if item_data.get('handler') else None,
                    operator_id=current_user_id,
                    remark=str(item_data.get('remark', '')) if item_data.get('remark') else None
                )
                
                db.session.add(record)
                
                item.quantity += quantity
                if unit_price > 0:
                    item.unit_price = unit_price
                
                success_count += 1
                
            except Exception as e:
                error_list.append(f'第{row_num}行: {str(e)}')
                continue
        
        if success_count > 0:
            db.session.commit()
            
            log = OperationLog(
                user_id=current_user_id,
                operation='批量入库',
                module='入库管理',
                description=f'批量入库成功{success_count}条记录，新建{new_item_count}个物品'
            )
            db.session.add(log)
            db.session.commit()
        
        return jsonify({
            'message': '导入完成',
            'success_count': success_count,
            'new_item_count': new_item_count,
            'error_count': len(error_list),
            'errors': error_list[:10]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'导入失败: {str(e)}'}), 500

@inbound_bp.route('/template', methods=['GET'])
@jwt_required()
def download_inbound_template():
    template_data = {
        '物品编码': ['ITM001', 'ITM002', 'ITM003'],
        '物品名称': ['螺丝刀', '扳手', '电缆线'],
        '数量': [100, 50, 200],
        '单价': [15.00, 25.00, 8.50],
        '来源': ['采购', '采购', '采购'],
        '供应商': ['五金工具厂', '五金工具厂', '电缆材料公司'],
        '经手人': ['张三', '张三', '张三'],
        '备注': ['', '', '']
    }
    
    df = pd.DataFrame(template_data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='批量入库模板')
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='批量入库模板.xlsx'
    )
