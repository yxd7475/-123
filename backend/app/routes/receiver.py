from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.models import Item, OutboundRecord, User
from app.utils.helpers import generate_record_no
from datetime import datetime

receiver_bp = Blueprint('receiver', __name__)

@receiver_bp.route('/items', methods=['GET'])
@jwt_required()
def get_receiver_items():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'receiver':
        return jsonify({'message': '无权访问'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    query = Item.query.filter(Item.quantity > 0, Item.status == True)
    
    if search:
        query = query.filter(
            (Item.name.contains(search)) |
            (Item.specification.contains(search))
        )
    
    if category:
        query = query.filter(Item.category == category)
    
    query = query.order_by(Item.name.asc())
    
    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'items': [item.to_dict() for item in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@receiver_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_receiver_categories():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'receiver':
        return jsonify({'message': '无权访问'}), 403
    
    categories = db.session.query(Item.category).filter(
        Item.category.isnot(None),
        Item.category != '',
        Item.quantity > 0,
        Item.status == True
    ).distinct().all()
    
    return jsonify({
        'categories': [cat[0] for cat in categories if cat[0]]
    }), 200

@receiver_bp.route('/receive', methods=['POST'])
@jwt_required()
def receive_item():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'receiver':
        return jsonify({'message': '无权访问'}), 403
    
    data = request.get_json()
    item_id = data.get('item_id')
    quantity = float(data.get('quantity', 0))
    purpose = data.get('purpose', '')
    
    if not item_id or quantity <= 0:
        return jsonify({'message': '参数错误'}), 400
    
    item = Item.query.get(item_id)
    if not item:
        return jsonify({'message': '物品不存在'}), 404
    
    if item.quantity < quantity:
        return jsonify({'message': '库存不足'}), 400
    
    record_no = generate_record_no('CK')
    
    record = OutboundRecord(
        record_no=record_no,
        item_id=item.id,
        item_code=item.item_code,
        item_name=item.name,
        outbound_type='receive',
        quantity=quantity,
        unit_price=item.unit_price,
        total_price=quantity * item.unit_price,
        receiver=user.real_name,
        operator_id=current_user_id,
        remark=purpose
    )
    
    item.quantity -= quantity
    
    db.session.add(record)
    db.session.commit()
    
    return jsonify({
        'message': '领取成功',
        'record_no': record_no
    }), 200

@receiver_bp.route('/records', methods=['GET'])
@jwt_required()
def get_receiver_records():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'receiver':
        return jsonify({'message': '无权访问'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = OutboundRecord.query.filter(
        OutboundRecord.operator_id == current_user_id,
        OutboundRecord.outbound_type == 'receive'
    ).order_by(OutboundRecord.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    records = []
    for record in pagination.items:
        record_dict = {
            'id': record.id,
            'record_no': record.record_no,
            'item_name': record.item_name,
            'quantity': record.quantity,
            'item_unit': None,
            'purpose': record.remark,
            'status': record.status,
            'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S') if record.created_at else None
        }
        item = Item.query.get(record.item_id)
        if item:
            record_dict['item_unit'] = item.unit
        records.append(record_dict)
    
    return jsonify({
        'records': records,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200
