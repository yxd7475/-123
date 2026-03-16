from flask import Blueprint, request, jsonify, send_file
from app import db
from app.models.models import Item, OutboundRecord
from app.utils.helpers import generate_record_no
from datetime import datetime, date
import pandas as pd
import io

public_bp = Blueprint('public', __name__)

@public_bp.route('/items', methods=['GET'])
def get_public_items():
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

@public_bp.route('/categories', methods=['GET'])
def get_public_categories():
    categories = db.session.query(Item.category).filter(
        Item.category.isnot(None),
        Item.category != '',
        Item.quantity > 0,
        Item.status == True
    ).distinct().all()
    
    return jsonify({
        'categories': [cat[0] for cat in categories if cat[0]]
    }), 200

@public_bp.route('/receive', methods=['POST'])
def public_receive():
    data = request.get_json()
    item_id = data.get('item_id')
    quantity = float(data.get('quantity', 0))
    receiver_name = data.get('receiver_name', '').strip()
    phone = data.get('phone', '')
    purpose = data.get('purpose', '')
    
    if not item_id or quantity <= 0:
        return jsonify({'message': '参数错误'}), 400
    
    if not receiver_name:
        return jsonify({'message': '请输入领取人姓名'}), 400
    
    item = Item.query.get(item_id)
    if not item:
        return jsonify({'message': '物品不存在'}), 404
    
    if item.quantity < quantity:
        return jsonify({'message': '库存不足'}), 400
    
    record_no = generate_record_no('CK')
    
    remark_parts = [f'领取人: {receiver_name}']
    if phone:
        remark_parts.append(f'电话: {phone}')
    if purpose:
        remark_parts.append(f'用途: {purpose}')
    
    record = OutboundRecord(
        record_no=record_no,
        item_id=item.id,
        item_code=item.item_code,
        item_name=item.name,
        outbound_type='public_receive',
        quantity=quantity,
        unit_price=item.unit_price,
        total_price=quantity * item.unit_price,
        receiver=receiver_name,
        remark=' | '.join(remark_parts)
    )
    
    item.quantity -= quantity
    
    db.session.add(record)
    db.session.commit()
    
    return jsonify({
        'message': '领取成功',
        'record_no': record_no
    }), 200

@public_bp.route('/records', methods=['GET'])
def get_public_records():
    receiver_name = request.args.get('receiver_name', '').strip()
    
    if not receiver_name:
        return jsonify({'records': []}), 200
    
    records = OutboundRecord.query.filter(
        OutboundRecord.receiver == receiver_name,
        OutboundRecord.outbound_type == 'public_receive'
    ).order_by(OutboundRecord.created_at.desc()).limit(50).all()
    
    result = []
    for record in records:
        record_dict = {
            'id': record.id,
            'record_no': record.record_no,
            'item_name': record.item_name,
            'quantity': record.quantity,
            'status': record.status,
            'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S') if record.created_at else None
        }
        
        if record.remark:
            parts = record.remark.split(' | ')
            for part in parts:
                if part.startswith('电话: '):
                    record_dict['phone'] = part.replace('电话: ', '')
                elif part.startswith('用途: '):
                    record_dict['purpose'] = part.replace('用途: ', '')
        
        item = Item.query.get(record.item_id)
        if item:
            record_dict['item_unit'] = item.unit
        
        result.append(record_dict)
    
    return jsonify({
        'records': result
    }), 200

@public_bp.route('/stats', methods=['GET'])
def get_public_stats():
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    
    today_receive = OutboundRecord.query.filter(
        OutboundRecord.outbound_type == 'public_receive',
        OutboundRecord.created_at >= today_start
    ).count()
    
    total_receive = OutboundRecord.query.filter(
        OutboundRecord.outbound_type == 'public_receive'
    ).count()
    
    available_items = Item.query.filter(
        Item.quantity > 0,
        Item.status == True
    ).count()
    
    return jsonify({
        'today_receive': today_receive,
        'total_receive': total_receive,
        'available_items': available_items
    }), 200

@public_bp.route('/export', methods=['GET'])
def export_public_records():
    records = OutboundRecord.query.filter(
        OutboundRecord.outbound_type == 'public_receive'
    ).order_by(OutboundRecord.created_at.desc()).all()
    
    data = []
    for record in records:
        phone = ''
        purpose = ''
        if record.remark:
            parts = record.remark.split(' | ')
            for part in parts:
                if part.startswith('电话: '):
                    phone = part.replace('电话: ', '')
                elif part.startswith('用途: '):
                    purpose = part.replace('用途: ', '')
        
        item = Item.query.get(record.item_id)
        
        data.append({
            '单号': record.record_no,
            '物品名称': record.item_name,
            '物品编码': record.item_code,
            '领取数量': record.quantity,
            '单位': item.unit if item else '',
            '领取人': record.receiver,
            '联系电话': phone,
            '领取用途': purpose,
            '领取时间': record.created_at.strftime('%Y-%m-%d %H:%M:%S') if record.created_at else ''
        })
    
    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='公开领取记录')
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'公开领取记录_{date.today().strftime("%Y%m%d")}.xlsx'
    )
