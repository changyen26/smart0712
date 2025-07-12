from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models import User

def admin_required(f):
    """需要管理員權限的裝飾器"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_admin:
            return jsonify({'message': '需要管理員權限'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def active_user_required(f):
    """需要啟用使用者的裝飾器"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': '使用者不存在'}), 404
        
        if not user.is_active:
            return jsonify({'message': '帳戶已被停用'}), 403
        
        return f(user, *args, **kwargs)
    return decorated_function

def get_current_user():
    """取得當前使用者"""
    try:
        current_user_id = get_jwt_identity()
        return User.query.get(current_user_id)
    except:
        return None

def token_required(optional=False):
    """Token 驗證裝飾器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if optional:
                try:
                    # 可選的 token 驗證
                    jwt_required(optional=True)
                    current_user = get_current_user()
                    return f(current_user, *args, **kwargs)
                except:
                    return f(None, *args, **kwargs)
            else:
                # 必須的 token 驗證
                jwt_required()
                current_user = get_current_user()
                if not current_user:
                    return jsonify({'message': '使用者不存在'}), 404
                return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator