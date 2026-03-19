from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app import db
from app.models.models import Item, OutboundRecord, OperationLog
from app.routes.auth import role_required
from app.utils.helpers import generate_record_no, check_inventory_alert, resolve_inventory_alerts
from datetime import datetime
import pandas as pd
import io

outbound_bp = Blueprint('outbound', __name__)

OUTBOUND_TYPES = {
    'sale': '销售出库',
    'requisition': '领用出库',
    'transfer': '调拨出库',
    'other': '其他出库'
}

ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

FIELD_MAPPING = {
    '物品编码': 'item_code',
    '编码': 'item_code',
    '物品名称': 'name',
    '名称': 'name',
    '数量': 'quantity',
    '领用数量': 'quantity',
    '领用人': 'receiver',
    '领取人': 'receiver',
    '去向': 'destination',
    '部门': 'destination',
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

@outbound_bp.route('', methods=['GET'])
@jwt_required()
def get_outbound_records():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    outbound_type = request.args.get('outbound_type', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    receiver = request.args.get('receiver', '')
    
    query = OutboundRecord.query
    
    if search:
        query = query.filter(
            (OutboundRecord.record_no.contains(search)) |
            (OutboundRecord.item_code.contains(search)) |
            (OutboundRecord.item_name.contains(search))
        )
    
    if outbound_type:
        query = query.filter(OutboundRecord.outbound_type == outbound_type)
    
    if start_date:
        query = query.filter(OutboundRecord.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
    
    if end_date:
        query = query.filter(OutboundRecord.created_at <= datetime.strptime(end_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S'))
    
    if receiver:
        query = query.filter(OutboundRecord.receiver.contains(receiver))
    
    pagination = query.order_by(OutboundRecord.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'records': [record.to_dict() for record in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@outbound_bp.route('/<int:record_id>', methods=['GET'])
@jwt_required()
def get_outbound_record(record_id):
    record = OutboundRecord.query.get(record_id)
    
    if not record:
        return jsonify({'message': '记录不存在'}), 404
    
    return jsonify(record.to_dict()), 200

@outbound_bp.route('', methods=['POST'])
@role_required('admin', 'operator')
def create_outbound_record():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    item_id = data.get('item_id')
    item = Item.query.get(item_id)
    
    if not item:
        return jsonify({'message': '物品不存在'}), 404
    
    quantity = float(data.get('quantity', 0))
    
    if quantity > item.quantity:
        return jsonify({'message': f'库存不足，当前库存: {item.quantity}'}), 400
    
    unit_price = float(data.get('unit_price', item.unit_price))
    total_price = quantity * unit_price
    
    record_no = generate_record_no('CK')
    
    record = OutboundRecord(
        record_no=record_no,
        item_id=item.id,
        item_code=item.item_code,
        item_name=item.name,
        outbound_type=data.get('outbound_type', 'normal'),
        quantity=quantity,
        unit_price=unit_price,
        total_price=total_price,
        destination=data.get('destination'),
        receiver=data.get('receiver'),
        handler=data.get('handler'),
        operator_id=current_user_id,
        remark=data.get('remark')
    )
    
    db.session.add(record)
    
    item.quantity -= quantity
    
    log = OperationLog(
        user_id=current_user_id,
        operation='出库',
        module='出库管理',
        description=f'出库单号: {record_no}, 物品: {item.name}, 数量: {quantity}'
    )
    db.session.add(log)
    
    db.session.commit()
    
    check_inventory_alert(item)
    resolve_inventory_alerts(item)
    
    return jsonify({
        'message': '出库成功',
        'record': record.to_dict()
    }), 201

@outbound_bp.route('/types', methods=['GET'])
@jwt_required()
def get_outbound_types():
    return jsonify(OUTBOUND_TYPES), 200

@outbound_bp.route('/import', methods=['POST'])
@role_required('admin', 'operator')
def batch_import_outbound():
    current_user_id = get_jwt_identity()
    
    if 'file' not in request.files:
        return jsonify({'message': '没有上传文件'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'message': '没有选择文件'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'message': '不支持的文件格式，请上传Excel或CSV文件'}), 400
    
    try:
        original_filename = file.filename
        file_ext = original_filename.rsplit('.', 1)[-1].lower() if '.' in original_filename else ''
        
        if not file_ext or file_ext not in ALLOWED_EXTENSIONS:
            return jsonify({'message': f'不支持的文件格式，请上传Excel或CSV文件（当前扩展名: {file_ext or "无"}）'}), 400
        
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
        insufficient_stock = []
        
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
                
                if item_code:
                    item = Item.query.filter_by(item_code=str(item_code)).first()
                else:
                    item = Item.query.filter_by(name=str(item_name)).first()
                
                if not item:
                    error_list.append(f'第{row_num}行: 物品不存在 ({item_code or item_name})')
                    continue
                
                quantity = float(item_data.get('quantity', 0))
                
                if quantity <= 0:
                    error_list.append(f'第{row_num}行: 数量必须大于0')
                    continue
                
                if quantity > item.quantity:
                    insufficient_stock.append({
                        'row': row_num,
                        'item': item.name,
                        'requested': quantity,
                        'available': item.quantity
                    })
                    continue
                
                unit_price = float(item.unit_price)
                total_price = quantity * unit_price
                
                record_no = generate_record_no('CK')
                
                record = OutboundRecord(
                    record_no=record_no,
                    item_id=item.id,
                    item_code=item.item_code,
                    item_name=item.name,
                    outbound_type='requisition',
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price,
                    destination=str(item_data.get('destination', '')) if item_data.get('destination') else None,
                    receiver=str(item_data.get('receiver', '')) if item_data.get('receiver') else None,
                    handler=str(item_data.get('handler', '')) if item_data.get('handler') else None,
                    operator_id=current_user_id,
                    remark=str(item_data.get('remark', '')) if item_data.get('remark') else None
                )
                
                db.session.add(record)
                
                item.quantity -= quantity
                
                success_count += 1
                
            except Exception as e:
                error_list.append(f'第{row_num}行: {str(e)}')
                continue
        
        if success_count > 0:
            db.session.commit()
            
            log = OperationLog(
                user_id=current_user_id,
                operation='批量出库',
                module='出库管理',
                description=f'批量出库成功{success_count}条记录'
            )
            db.session.add(log)
            db.session.commit()
        
        return jsonify({
            'message': '导入完成',
            'success_count': success_count,
            'error_count': len(error_list),
            'insufficient_count': len(insufficient_stock),
            'errors': error_list[:10],
            'insufficient_stock': insufficient_stock[:10]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'导入失败: {str(e)}'}), 500

@outbound_bp.route('/export', methods=['GET'])
@jwt_required()
def export_outbound_records():
    search = request.args.get('search', '')
    outbound_type = request.args.get('outbound_type', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    receiver = request.args.get('receiver', '')
    
    query = OutboundRecord.query
    
    if search:
        query = query.filter(
            (OutboundRecord.record_no.contains(search)) |
            (OutboundRecord.item_code.contains(search)) |
            (OutboundRecord.item_name.contains(search))
        )
    
    if outbound_type:
        query = query.filter(OutboundRecord.outbound_type == outbound_type)
    
    if start_date:
        query = query.filter(OutboundRecord.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
    
    if end_date:
        query = query.filter(OutboundRecord.created_at <= datetime.strptime(end_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S'))
    
    if receiver:
        query = query.filter(OutboundRecord.receiver.contains(receiver))
    
    records = query.order_by(OutboundRecord.created_at.desc()).all()
    
    data = []
    for record in records:
        data.append({
            '出库单号': record.record_no,
            '物品编码': record.item_code,
            '物品名称': record.item_name,
            '出库类型': OUTBOUND_TYPES.get(record.outbound_type, record.outbound_type),
            '数量': record.quantity,
            '单价': record.unit_price,
            '总价': record.total_price,
            '去向': record.destination or '',
            '领用人': record.receiver or '',
            '经手人': record.handler or '',
            '出库时间': record.created_at.strftime('%Y-%m-%d %H:%M:%S') if record.created_at else '',
            '备注': record.remark or ''
        })
    
    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='出库记录')
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'出库记录_{datetime.now().strftime("%Y%m%d")}.xlsx'
    )

@outbound_bp.route('/template', methods=['GET'])
@jwt_required()
def download_outbound_template():
    template_data = {
        '物品编码': ['ITM001', 'ITM002', 'ITM003'],
        '物品名称': ['螺丝刀', '扳手', '电缆线'],
        '领用数量': [5, 3, 20],
        '领用人': ['张三', '李四', '王五'],
        '去向/部门': ['维修部', '生产部', '工程部'],
        '经手人': ['赵六', '赵六', '赵六'],
        '备注': ['', '', '']
    }
    
    df = pd.DataFrame(template_data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='批量出库模板')
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='批量出库模板.xlsx'
    )
