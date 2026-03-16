from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from app.models.models import User, OperationLog
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            if not user or user.role not in roles:
                return jsonify({'message': '权限不足'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': '用户名和密码不能为空'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': '用户名或密码错误'}), 401
    
    if not user.status:
        return jsonify({'message': '账户已被禁用'}), 403
    
    access_token = create_access_token(identity=user.id)
    
    log = OperationLog(
        user_id=user.id,
        username=user.username,
        operation='登录',
        module='认证',
        description=f'用户 {user.real_name} 登录系统',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'message': '登录成功',
        'token': access_token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user:
        log = OperationLog(
            user_id=user.id,
            username=user.username,
            operation='登出',
            module='认证',
            description=f'用户 {user.real_name} 退出系统',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
    
    return jsonify({'message': '登出成功'}), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    return jsonify(user.to_dict()), 200

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    data = request.get_json()
    real_name = data.get('real_name')
    
    if real_name:
        user.real_name = real_name
        db.session.commit()
        
        log = OperationLog(
            user_id=user.id,
            username=user.username,
            operation='修改资料',
            module='用户',
            description=f'用户修改了个人信息',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
    
    return jsonify({'message': '保存成功', **user.to_dict()}), 200

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({'message': '请填写完整信息'}), 400
    
    if not check_password_hash(user.password, old_password):
        return jsonify({'message': '原密码错误'}), 400
    
    user.password = generate_password_hash(new_password)
    
    log = OperationLog(
        user_id=user.id,
        username=user.username,
        operation='修改密码',
        module='用户',
        description=f'用户修改了登录密码',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': '密码修改成功'}), 200
