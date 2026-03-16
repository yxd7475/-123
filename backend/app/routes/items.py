from flask import Blueprint, request, jsonify, send_file, send_from_directory, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app import db
from app.models.models import Item, OperationLog
from app.routes.auth import role_required
from datetime import datetime
from pypinyin import lazy_pinyin
import pandas as pd
import os
import io
import re
import uuid

items_bp = Blueprint('items', __name__)

ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
UPLOAD_FOLDER = 'uploads'

FIELD_MAPPING = {
    '物品编码': 'item_code',
    '编码': 'item_code',
    '物品名称': 'name',
    '名称': 'name',
    '规格': 'specification',
    '规格型号': 'specification',
    '型号': 'model',
    '属性': 'attribute',
    '品牌': 'brand',
    '单位': 'unit',
    '单价': 'unit_price',
    '价格': 'unit_price',
    '库存数量': 'quantity',
    '数量': 'quantity',
    '库存': 'quantity',
    '库存下限': 'min_quantity',
    '下限': 'min_quantity',
    '库存上限': 'max_quantity',
    '上限': 'max_quantity',
    '分类': 'category',
    '类别': 'category',
    '存放位置': 'location',
    '位置': 'location',
    '供应商': 'supplier',
    '备注': 'remark',
    '说明': 'remark'
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

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

def generate_item_code(index):
    return f'AUTO{datetime.now().strftime("%Y%m%d")}{str(index).zfill(4)}'

@items_bp.route('', methods=['GET'])
@jwt_required()
def get_items():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    status = request.args.get('status', '')
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'asc')
    
    query = Item.query
    
    if search:
        query = query.filter(
            (Item.item_code.contains(search)) |
            (Item.name.contains(search)) |
            (Item.specification.contains(search))
        )
    
    if category:
        query = query.filter(Item.category == category)
    
    if status:
        query = query.filter(Item.status == (status == 'true'))
    
    if sort_by == 'name':
        all_items = query.all()
        all_items.sort(key=lambda x: ''.join(lazy_pinyin(x.name or '')), reverse=(sort_order == 'desc'))
        total = len(all_items)
        start = (page - 1) * per_page
        end = start + per_page
        items_page = all_items[start:end]
        
        return jsonify({
            'items': [item.to_dict() for item in items_page],
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'current_page': page
        }), 200
    else:
        sort_column = getattr(Item, sort_by, Item.name)
        if sort_order == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'items': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200

@items_bp.route('/<int:item_id>', methods=['GET'])
@jwt_required()
def get_item(item_id):
    item = Item.query.get(item_id)
    
    if not item:
        return jsonify({'message': '物品不存在'}), 404
    
    return jsonify(item.to_dict()), 200

@items_bp.route('', methods=['POST'])
@role_required('admin', 'operator')
def create_item():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if Item.query.filter_by(item_code=data.get('item_code')).first():
        return jsonify({'message': '物品编码已存在'}), 400
    
    item = Item(
        item_code=data.get('item_code'),
        name=data.get('name'),
        specification=data.get('specification'),
        model=data.get('model'),
        attribute=data.get('attribute'),
        brand=data.get('brand'),
        unit=data.get('unit'),
        unit_price=data.get('unit_price', 0),
        quantity=data.get('quantity', 0),
        min_quantity=data.get('min_quantity', 10),
        max_quantity=data.get('max_quantity', 1000),
        category=data.get('category'),
        location=data.get('location'),
        supplier=data.get('supplier'),
        remark=data.get('remark')
    )
    
    db.session.add(item)
    
    log = OperationLog(
        user_id=current_user_id,
        operation='创建物品',
        module='物品管理',
        description=f'创建物品: {item.name} ({item.item_code})'
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': '创建成功', 'item': item.to_dict()}), 201

@items_bp.route('/<int:item_id>', methods=['PUT'])
@role_required('admin', 'operator')
def update_item(item_id):
    current_user_id = get_jwt_identity()
    item = Item.query.get(item_id)
    
    if not item:
        return jsonify({'message': '物品不存在'}), 404
    
    data = request.get_json()
    
    if data.get('item_code') and data.get('item_code') != item.item_code:
        if Item.query.filter_by(item_code=data.get('item_code')).first():
            return jsonify({'message': '物品编码已存在'}), 400
        item.item_code = data.get('item_code')
    
    for field in ['name', 'specification', 'model', 'attribute', 'brand', 'unit', 'unit_price', 
                  'min_quantity', 'max_quantity', 'category', 'location', 
                  'supplier', 'image', 'remark', 'status']:
        if field in data:
            setattr(item, field, data[field])
    
    log = OperationLog(
        user_id=current_user_id,
        operation='更新物品',
        module='物品管理',
        description=f'更新物品: {item.name} ({item.item_code})'
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': '更新成功', 'item': item.to_dict()}), 200

@items_bp.route('/<int:item_id>', methods=['DELETE'])
@role_required('admin')
def delete_item(item_id):
    current_user_id = get_jwt_identity()
    item = Item.query.get(item_id)
    
    if not item:
        return jsonify({'message': '物品不存在'}), 404
    
    item_name = item.name
    item_code = item.item_code
    
    db.session.delete(item)
    
    log = OperationLog(
        user_id=current_user_id,
        operation='删除物品',
        module='物品管理',
        description=f'删除物品: {item_name} ({item_code})'
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': '删除成功'}), 200

@items_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    categories = db.session.query(Item.category).distinct().all()
    return jsonify([c[0] for c in categories if c[0]]), 200

@items_bp.route('/import', methods=['POST'])
@role_required('admin', 'operator')
def import_items():
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
        skip_count = 0
        
        for index, row in df.iterrows():
            row_num = index + 2
            
            try:
                item_data = {}
                for col, field in column_mapping.items():
                    if col in df.columns and pd.notna(row[col]):
                        item_data[field] = row[col]
                
                if 'name' not in item_data or not item_data['name']:
                    error_list.append(f'第{row_num}行: 缺少物品名称')
                    continue
                
                item_code = item_data.get('item_code', '')
                if not item_code or str(item_code).strip() == '' or str(item_code).lower() == 'nan':
                    item_code = generate_item_code(success_count + 1)
                    item_data['item_code'] = item_code
                
                existing_item = Item.query.filter_by(item_code=str(item_code)).first()
                if existing_item:
                    skip_count += 1
                    continue
                
                def parse_float(value, default=0):
                    try:
                        if pd.isna(value):
                            return default
                        return float(value)
                    except:
                        return default
                
                item = Item(
                    item_code=str(item_code),
                    name=str(item_data.get('name', '')),
                    specification=str(item_data.get('specification', '')) if item_data.get('specification') else None,
                    model=str(item_data.get('model', '')) if item_data.get('model') else None,
                    attribute=str(item_data.get('attribute', '')) if item_data.get('attribute') else None,
                    brand=str(item_data.get('brand', '')) if item_data.get('brand') else None,
                    unit=str(item_data.get('unit', '个')) if item_data.get('unit') else '个',
                    unit_price=parse_float(item_data.get('unit_price', 0)),
                    quantity=parse_float(item_data.get('quantity', 0)),
                    min_quantity=parse_float(item_data.get('min_quantity', 10)),
                    max_quantity=parse_float(item_data.get('max_quantity', 1000)),
                    category=str(item_data.get('category', '')) if item_data.get('category') else None,
                    location=str(item_data.get('location', '')) if item_data.get('location') else None,
                    supplier=str(item_data.get('supplier', '')) if item_data.get('supplier') else None,
                    remark=str(item_data.get('remark', '')) if item_data.get('remark') else None
                )
                
                db.session.add(item)
                success_count += 1
                
            except Exception as e:
                error_list.append(f'第{row_num}行: {str(e)}')
                continue
        
        db.session.commit()
        
        log = OperationLog(
            user_id=current_user_id,
            operation='导入物品',
            module='物品管理',
            description=f'成功导入{success_count}个物品，跳过{skip_count}个重复物品'
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'message': '导入完成',
            'success_count': success_count,
            'skip_count': skip_count,
            'error_count': len(error_list),
            'errors': error_list[:10]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'导入失败: {str(e)}'}), 500

@items_bp.route('/template', methods=['GET'])
@jwt_required()
def download_template():
    template_data = {
        '物品编码': ['ITM001', 'ITM002', 'ITM003'],
        '物品名称': ['螺丝刀', '扳手', '电缆线'],
        '规格': ['M6*100mm', '8寸', '3*2.5mm²'],
        '型号': ['SD-001', 'BW-008', 'DL-0025'],
        '属性': ['', '', ''],
        '品牌': ['得力', '世达', '远东'],
        '单位': ['把', '把', '米'],
        '单价': [15.00, 25.00, 8.50],
        '库存数量': [100, 50, 500],
        '库存下限': [20, 10, 100],
        '库存上限': [500, 200, 2000],
        '分类': ['工具类', '工具类', '电气类'],
        '存放位置': ['A区-01货架-01层', 'A区-01货架-02层', 'B区-02货架-01层'],
        '供应商': ['五金工具厂', '五金工具厂', '电缆材料公司'],
        '备注': ['', '', '']
    }
    
    df = pd.DataFrame(template_data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='物品导入模板')
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='物品导入模板.xlsx'
    )

@items_bp.route('/upload-image', methods=['POST'])
@jwt_required()
def upload_image():
    if 'file' not in request.files:
        return jsonify({'message': '没有上传文件'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'message': '没有选择文件'}), 400
    
    if not allowed_image(file.filename):
        return jsonify({'message': '不支持的图片格式，请上传 png/jpg/jpeg/gif/webp 格式'}), 400
    
    try:
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), UPLOAD_FOLDER)
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        return jsonify({
            'message': '上传成功',
            'filename': filename,
            'url': f'/api/items/images/{filename}'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'上传失败: {str(e)}'}), 500

@items_bp.route('/images/<filename>', methods=['GET'])
def get_image(filename):
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), UPLOAD_FOLDER)
    return send_from_directory(upload_dir, filename)
