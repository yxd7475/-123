from datetime import datetime
from app import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    real_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='operator')
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'real_name': self.real_name,
            'role': self.role,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class Item(db.Model):
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    item_code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    specification = db.Column(db.String(100))
    model = db.Column(db.String(50))
    attribute = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    unit = db.Column(db.String(20), nullable=False)
    unit_price = db.Column(db.Float, nullable=False, default=0)
    quantity = db.Column(db.Float, nullable=False, default=0)
    min_quantity = db.Column(db.Float, default=10)
    max_quantity = db.Column(db.Float, default=1000)
    category = db.Column(db.String(50))
    location = db.Column(db.String(100))
    supplier = db.Column(db.String(100))
    image = db.Column(db.String(255))
    remark = db.Column(db.Text)
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'item_code': self.item_code,
            'name': self.name,
            'specification': self.specification,
            'model': self.model,
            'attribute': self.attribute,
            'brand': self.brand,
            'unit': self.unit,
            'unit_price': self.unit_price,
            'quantity': self.quantity,
            'min_quantity': self.min_quantity,
            'max_quantity': self.max_quantity,
            'category': self.category,
            'location': self.location,
            'supplier': self.supplier,
            'image': self.image,
            'remark': self.remark,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class InboundRecord(db.Model):
    __tablename__ = 'inbound_records'
    
    id = db.Column(db.Integer, primary_key=True)
    record_no = db.Column(db.String(50), unique=True, nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    item_code = db.Column(db.String(50), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    inbound_type = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False, default=0)
    total_price = db.Column(db.Float, nullable=False, default=0)
    source = db.Column(db.String(100))
    supplier = db.Column(db.String(100))
    handler = db.Column(db.String(50))
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    remark = db.Column(db.Text)
    status = db.Column(db.String(20), default='completed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    item = db.relationship('Item', backref='inbound_records')
    operator = db.relationship('User', backref='inbound_records')
    
    def to_dict(self):
        return {
            'id': self.id,
            'record_no': self.record_no,
            'item_id': self.item_id,
            'item_code': self.item_code,
            'item_name': self.item_name,
            'inbound_type': self.inbound_type,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_price': self.total_price,
            'source': self.source,
            'supplier': self.supplier,
            'handler': self.handler,
            'operator_id': self.operator_id,
            'remark': self.remark,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class OutboundRecord(db.Model):
    __tablename__ = 'outbound_records'
    
    id = db.Column(db.Integer, primary_key=True)
    record_no = db.Column(db.String(50), unique=True, nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    item_code = db.Column(db.String(50), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    outbound_type = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False, default=0)
    total_price = db.Column(db.Float, nullable=False, default=0)
    destination = db.Column(db.String(100))
    receiver = db.Column(db.String(50))
    handler = db.Column(db.String(50))
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    remark = db.Column(db.Text)
    status = db.Column(db.String(20), default='completed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    item = db.relationship('Item', backref='outbound_records')
    operator = db.relationship('User', backref='outbound_records')
    
    def to_dict(self):
        return {
            'id': self.id,
            'record_no': self.record_no,
            'item_id': self.item_id,
            'item_code': self.item_code,
            'item_name': self.item_name,
            'outbound_type': self.outbound_type,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_price': self.total_price,
            'destination': self.destination,
            'receiver': self.receiver,
            'handler': self.handler,
            'operator_id': self.operator_id,
            'remark': self.remark,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class InventoryAlert(db.Model):
    __tablename__ = 'inventory_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    item_code = db.Column(db.String(50), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    alert_type = db.Column(db.String(20), nullable=False)
    current_quantity = db.Column(db.Float, nullable=False)
    threshold = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    item = db.relationship('Item', backref='alerts')
    
    def to_dict(self):
        return {
            'id': self.id,
            'item_id': self.item_id,
            'item_code': self.item_code,
            'item_name': self.item_name,
            'alert_type': self.alert_type,
            'current_quantity': self.current_quantity,
            'threshold': self.threshold,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'resolved_at': self.resolved_at.strftime('%Y-%m-%d %H:%M:%S') if self.resolved_at else None
        }

class OperationLog(db.Model):
    __tablename__ = 'operation_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    username = db.Column(db.String(50))
    operation = db.Column(db.String(50), nullable=False)
    module = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='logs')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'operation': self.operation,
            'module': self.module,
            'description': self.description,
            'ip_address': self.ip_address,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
