from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.models import Item, InventoryAlert
from datetime import datetime

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('', methods=['GET'])
@jwt_required()
def get_inventory():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    alert_status = request.args.get('alert_status', '')
    
    query = Item.query.filter(Item.status == True)
    
    if search:
        query = query.filter(
            (Item.item_code.contains(search)) |
            (Item.name.contains(search))
        )
    
    if category:
        query = query.filter(Item.category == category)
    
    items = query.order_by(Item.created_at.desc()).all()
    
    inventory_list = []
    for item in items:
        alert_level = 'normal'
        if item.quantity <= item.min_quantity:
            alert_level = 'low'
        elif item.quantity >= item.max_quantity:
            alert_level = 'high'
        
        if alert_status == 'low' and alert_level != 'low':
            continue
        if alert_status == 'high' and alert_level != 'high':
            continue
        if alert_status == 'normal' and alert_level != 'normal':
            continue
        
        inventory_list.append({
            **item.to_dict(),
            'alert_level': alert_level
        })
    
    total = len(inventory_list)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_list = inventory_list[start:end]
    
    return jsonify({
        'inventory': paginated_list,
        'total': total,
        'pages': (total + per_page - 1) // per_page,
        'current_page': page
    }), 200

@inventory_bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_alerts():
    status = request.args.get('status', 'pending')
    
    query = InventoryAlert.query
    
    if status:
        query = query.filter(InventoryAlert.status == status)
    
    alerts = query.order_by(InventoryAlert.created_at.desc()).all()
    
    return jsonify({
        'alerts': [alert.to_dict() for alert in alerts],
        'total': len(alerts)
    }), 200

@inventory_bp.route('/alerts/<int:alert_id>/resolve', methods=['POST'])
@jwt_required()
def resolve_alert(alert_id):
    alert = InventoryAlert.query.get(alert_id)
    
    if not alert:
        return jsonify({'message': '预警不存在'}), 404
    
    alert.status = 'resolved'
    alert.resolved_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': '预警已处理'}), 200

@inventory_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_inventory_summary():
    total_items = Item.query.filter(Item.status == True).count()
    total_quantity = db.session.query(db.func.sum(Item.quantity)).filter(Item.status == True).scalar() or 0
    total_value = db.session.query(db.func.sum(Item.quantity * Item.unit_price)).filter(Item.status == True).scalar() or 0
    
    low_stock_count = Item.query.filter(
        Item.status == True,
        Item.quantity <= Item.min_quantity
    ).count()
    
    high_stock_count = Item.query.filter(
        Item.status == True,
        Item.quantity >= Item.max_quantity
    ).count()
    
    pending_alerts = InventoryAlert.query.filter(InventoryAlert.status == 'pending').count()
    
    return jsonify({
        'total_items': total_items,
        'total_quantity': total_quantity,
        'total_value': float(total_value),
        'low_stock_count': low_stock_count,
        'high_stock_count': high_stock_count,
        'pending_alerts': low_stock_count + high_stock_count
    }), 200
