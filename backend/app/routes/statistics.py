from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.models import Item, InboundRecord, OutboundRecord
from sqlalchemy import func
from datetime import datetime, timedelta

statistics_bp = Blueprint('statistics', __name__)

@statistics_bp.route('/overview', methods=['GET'])
@jwt_required()
def get_overview():
    today = datetime.now().date()
    month_start = today.replace(day=1)
    
    total_inbound_today = db.session.query(func.sum(InboundRecord.quantity)).filter(
        func.date(InboundRecord.created_at) == today
    ).scalar() or 0
    
    total_outbound_today = db.session.query(func.sum(OutboundRecord.quantity)).filter(
        func.date(OutboundRecord.created_at) == today
    ).scalar() or 0
    
    total_inbound_month = db.session.query(func.sum(InboundRecord.quantity)).filter(
        InboundRecord.created_at >= month_start
    ).scalar() or 0
    
    total_outbound_month = db.session.query(func.sum(OutboundRecord.quantity)).filter(
        OutboundRecord.created_at >= month_start
    ).scalar() or 0
    
    total_inbound_value_month = db.session.query(func.sum(InboundRecord.total_price)).filter(
        InboundRecord.created_at >= month_start
    ).scalar() or 0
    
    total_outbound_value_month = db.session.query(func.sum(OutboundRecord.total_price)).filter(
        OutboundRecord.created_at >= month_start
    ).scalar() or 0
    
    return jsonify({
        'today': {
            'inbound_quantity': float(total_inbound_today),
            'outbound_quantity': float(total_outbound_today)
        },
        'month': {
            'inbound_quantity': float(total_inbound_month),
            'outbound_quantity': float(total_outbound_month),
            'inbound_value': float(total_inbound_value_month),
            'outbound_value': float(total_outbound_value_month)
        }
    }), 200

@statistics_bp.route('/trend', methods=['GET'])
@jwt_required()
def get_trend():
    days = request.args.get('days', 7, type=int)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)
    
    trend_data = []
    current_date = start_date
    
    while current_date <= end_date:
        inbound_qty = db.session.query(func.sum(InboundRecord.quantity)).filter(
            func.date(InboundRecord.created_at) == current_date
        ).scalar() or 0
        
        outbound_qty = db.session.query(func.sum(OutboundRecord.quantity)).filter(
            func.date(OutboundRecord.created_at) == current_date
        ).scalar() or 0
        
        trend_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'inbound': float(inbound_qty),
            'outbound': float(outbound_qty)
        })
        
        current_date += timedelta(days=1)
    
    return jsonify(trend_data), 200

@statistics_bp.route('/category', methods=['GET'])
@jwt_required()
def get_category_statistics():
    category_stats = db.session.query(
        Item.category,
        func.count(Item.id).label('item_count'),
        func.sum(Item.quantity).label('total_quantity'),
        func.sum(Item.quantity * Item.unit_price).label('total_value')
    ).filter(Item.status == True).group_by(Item.category).all()
    
    result = []
    for stat in category_stats:
        if stat.category:
            result.append({
                'category': stat.category,
                'item_count': stat.item_count,
                'total_quantity': float(stat.total_quantity or 0),
                'total_value': float(stat.total_value or 0)
            })
    
    return jsonify(result), 200

@statistics_bp.route('/inbound-type', methods=['GET'])
@jwt_required()
def get_inbound_type_statistics():
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    query = db.session.query(
        InboundRecord.inbound_type,
        func.count(InboundRecord.id).label('record_count'),
        func.sum(InboundRecord.quantity).label('total_quantity'),
        func.sum(InboundRecord.total_price).label('total_value')
    )
    
    if start_date:
        query = query.filter(InboundRecord.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(InboundRecord.created_at <= datetime.strptime(end_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S'))
    
    stats = query.group_by(InboundRecord.inbound_type).all()
    
    result = []
    for stat in stats:
        result.append({
            'type': stat.inbound_type,
            'record_count': stat.record_count,
            'total_quantity': float(stat.total_quantity or 0),
            'total_value': float(stat.total_value or 0)
        })
    
    return jsonify(result), 200

@statistics_bp.route('/outbound-type', methods=['GET'])
@jwt_required()
def get_outbound_type_statistics():
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    query = db.session.query(
        OutboundRecord.outbound_type,
        func.count(OutboundRecord.id).label('record_count'),
        func.sum(OutboundRecord.quantity).label('total_quantity'),
        func.sum(OutboundRecord.total_price).label('total_value')
    )
    
    if start_date:
        query = query.filter(OutboundRecord.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(OutboundRecord.created_at <= datetime.strptime(end_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S'))
    
    stats = query.group_by(OutboundRecord.outbound_type).all()
    
    result = []
    for stat in stats:
        result.append({
            'type': stat.outbound_type,
            'record_count': stat.record_count,
            'total_quantity': float(stat.total_quantity or 0),
            'total_value': float(stat.total_value or 0)
        })
    
    return jsonify(result), 200

@statistics_bp.route('/top-items', methods=['GET'])
@jwt_required()
def get_top_items():
    limit = request.args.get('limit', 10, type=int)
    stat_type = request.args.get('type', 'inbound')
    
    if stat_type == 'inbound':
        stats = db.session.query(
            InboundRecord.item_id,
            InboundRecord.item_code,
            InboundRecord.item_name,
            func.sum(InboundRecord.quantity).label('total_quantity')
        ).group_by(InboundRecord.item_id, InboundRecord.item_code, InboundRecord.item_name).order_by(
            func.sum(InboundRecord.quantity).desc()
        ).limit(limit).all()
    else:
        stats = db.session.query(
            OutboundRecord.item_id,
            OutboundRecord.item_code,
            OutboundRecord.item_name,
            func.sum(OutboundRecord.quantity).label('total_quantity')
        ).group_by(OutboundRecord.item_id, OutboundRecord.item_code, OutboundRecord.item_name).order_by(
            func.sum(OutboundRecord.quantity).desc()
        ).limit(limit).all()
    
    result = []
    for stat in stats:
        result.append({
            'item_id': stat.item_id,
            'item_code': stat.item_code,
            'item_name': stat.item_name,
            'total_quantity': float(stat.total_quantity or 0)
        })
    
    return jsonify(result), 200
