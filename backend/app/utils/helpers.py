import random
from datetime import datetime

def generate_record_no(prefix):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_num = random.randint(1000, 9999)
    return f'{prefix}{timestamp}{random_num}'

def check_inventory_alert(item):
    from app import db
    from app.models.models import InventoryAlert
    
    alerts = []
    
    if item.quantity <= item.min_quantity:
        existing_alert = InventoryAlert.query.filter_by(
            item_id=item.id,
            alert_type='low',
            status='pending'
        ).first()
        
        if not existing_alert:
            alert = InventoryAlert(
                item_id=item.id,
                item_code=item.item_code,
                item_name=item.name,
                alert_type='low',
                current_quantity=item.quantity,
                threshold=item.min_quantity,
                status='pending'
            )
            db.session.add(alert)
            alerts.append(alert)
    
    if item.quantity >= item.max_quantity:
        existing_alert = InventoryAlert.query.filter_by(
            item_id=item.id,
            alert_type='high',
            status='pending'
        ).first()
        
        if not existing_alert:
            alert = InventoryAlert(
                item_id=item.id,
                item_code=item.item_code,
                item_name=item.name,
                alert_type='high',
                current_quantity=item.quantity,
                threshold=item.max_quantity,
                status='pending'
            )
            db.session.add(alert)
            alerts.append(alert)
    
    if alerts:
        db.session.commit()
    
    return alerts

def resolve_inventory_alerts(item):
    from app import db
    from app.models.models import InventoryAlert
    
    pending_alerts = InventoryAlert.query.filter_by(
        item_id=item.id,
        status='pending'
    ).all()
    
    for alert in pending_alerts:
        if alert.alert_type == 'low' and item.quantity > item.min_quantity:
            alert.status = 'resolved'
            alert.resolved_at = datetime.utcnow()
        elif alert.alert_type == 'high' and item.quantity < item.max_quantity:
            alert.status = 'resolved'
            alert.resolved_at = datetime.utcnow()
    
    db.session.commit()
