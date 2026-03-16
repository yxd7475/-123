from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from app import db
from app.routes.auth import role_required
import os
import shutil
from datetime import datetime
import json

backup_bp = Blueprint('backup', __name__)

BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'instance', 'backups')

@backup_bp.route('', methods=['GET'])
@role_required('admin')
def get_backups():
    try:
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
        
        backups = []
        for filename in os.listdir(BACKUP_DIR):
            if filename.endswith('.db'):
                filepath = os.path.join(BACKUP_DIR, filename)
                stat = os.stat(filepath)
                backups.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'created_at': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({'backups': backups}), 200
    except Exception as e:
        return jsonify({'message': f'获取备份列表失败: {str(e)}'}), 500

@backup_bp.route('', methods=['POST'])
@role_required('admin')
def create_backup():
    try:
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
        
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'instance', 'warehouse.db')
        
        if not os.path.exists(db_path):
            return jsonify({'message': '数据库文件不存在'}), 404
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'warehouse_backup_{timestamp}.db'
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        shutil.copy2(db_path, backup_path)
        
        return jsonify({
            'message': '备份成功',
            'filename': backup_filename
        }), 200
    except Exception as e:
        return jsonify({'message': f'备份失败: {str(e)}'}), 500

@backup_bp.route('/<filename>/restore', methods=['POST'])
@role_required('admin')
def restore_backup(filename):
    try:
        backup_path = os.path.join(BACKUP_DIR, filename)
        
        if not os.path.exists(backup_path):
            return jsonify({'message': '备份文件不存在'}), 404
        
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'instance', 'warehouse.db')
        
        db.session.close()
        
        shutil.copy2(backup_path, db_path)
        
        return jsonify({'message': '恢复成功，请重启服务器'}), 200
    except Exception as e:
        return jsonify({'message': f'恢复失败: {str(e)}'}), 500

@backup_bp.route('/<filename>', methods=['DELETE'])
@role_required('admin')
def delete_backup(filename):
    try:
        backup_path = os.path.join(BACKUP_DIR, filename)
        
        if not os.path.exists(backup_path):
            return jsonify({'message': '备份文件不存在'}), 404
        
        os.remove(backup_path)
        
        return jsonify({'message': '删除成功'}), 200
    except Exception as e:
        return jsonify({'message': f'删除失败: {str(e)}'}), 500

@backup_bp.route('/<filename>/download', methods=['GET'])
@role_required('admin')
def download_backup(filename):
    try:
        backup_path = os.path.join(BACKUP_DIR, filename)
        
        if not os.path.exists(backup_path):
            return jsonify({'message': '备份文件不存在'}), 404
        
        return send_file(backup_path, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'message': f'下载失败: {str(e)}'}), 500
