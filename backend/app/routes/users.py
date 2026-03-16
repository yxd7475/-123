from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from app import db
from app.models.models import User, OperationLog
from app.routes.auth import role_required

users_bp = Blueprint('users', __name__)

@users_bp.route('', methods=['GET'])
@role_required('admin')
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    role = request.args.get('role', '')
    
    query = User.query
    
    if search:
        query = query.filter(
            (User.username.contains(search)) |
            (User.real_name.contains(search))
        )
    
    if role:
        query = query.filter(User.role == role)
    
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'users': [user.to_dict() for user in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@users_bp.route('/<int:user_id>', methods=['GET'])
@role_required('admin')
def get_user(user_id):
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    return jsonify(user.to_dict()), 200

@users_bp.route('', methods=['POST'])
@role_required('admin')
def create_user():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({'message': '用户名已存在'}), 400
    
    user = User(
        username=data.get('username'),
        password=generate_password_hash(data.get('password')),
        real_name=data.get('real_name'),
        role=data.get('role', 'operator'),
        status=data.get('status', True)
    )
    
    db.session.add(user)
    
    log = OperationLog(
        user_id=current_user_id,
        operation='创建用户',
        module='用户管理',
        description=f'创建用户: {user.username} ({user.real_name})'
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': '创建成功', 'user': user.to_dict()}), 201

@users_bp.route('/<int:user_id>', methods=['PUT'])
@role_required('admin')
def update_user(user_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    data = request.get_json()
    
    if data.get('username') and data.get('username') != user.username:
        if User.query.filter_by(username=data.get('username')).first():
            return jsonify({'message': '用户名已存在'}), 400
        user.username = data.get('username')
    
    if data.get('password'):
        user.password = generate_password_hash(data.get('password'))
    
    for field in ['real_name', 'role', 'status']:
        if field in data:
            setattr(user, field, data[field])
    
    log = OperationLog(
        user_id=current_user_id,
        operation='更新用户',
        module='用户管理',
        description=f'更新用户: {user.username}'
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': '更新成功', 'user': user.to_dict()}), 200

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@role_required('admin')
def delete_user(user_id):
    current_user_id = get_jwt_identity()
    
    if user_id == current_user_id:
        return jsonify({'message': '不能删除自己的账户'}), 400
    
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    if user.username == 'admin':
        return jsonify({'message': '不能删除管理员账户'}), 400
    
    username = user.username
    db.session.delete(user)
    
    log = OperationLog(
        user_id=current_user_id,
        operation='删除用户',
        module='用户管理',
        description=f'删除用户: {username}'
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': '删除成功'}), 200

@users_bp.route('/roles', methods=['GET'])
@jwt_required()
def get_roles():
    roles = [
        {'value': 'admin', 'label': '管理员'},
        {'value': 'operator', 'label': '操作员'},
        {'value': 'viewer', 'label': '查看员'}
    ]
    return jsonify(roles), 200

@users_bp.route('/logs', methods=['GET'])
@role_required('admin')
def get_operation_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    user_id = request.args.get('user_id', '')
    module = request.args.get('module', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    query = OperationLog.query
    
    if user_id:
        query = query.filter(OperationLog.user_id == user_id)
    
    if module:
        query = query.filter(OperationLog.module == module)
    
    if start_date:
        query = query.filter(OperationLog.created_at >= start_date)
    
    if end_date:
        query = query.filter(OperationLog.created_at <= end_date + ' 23:59:59')
    
    pagination = query.order_by(OperationLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'logs': [log.to_dict() for log in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200
