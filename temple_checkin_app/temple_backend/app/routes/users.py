from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User
from app.utils.helpers import success_response, error_response, safe_get_json
from app.utils.auth import active_user_required

users_bp = Blueprint('users', __name__, url_prefix='/api/users')

@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """取得使用者個人資料"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return error_response('使用者不存在', status_code=404)
        
        return success_response(user.to_dict(include_sensitive=True))
        
    except Exception as e:
        return error_response(f'取得個人資料失敗: {str(e)}', status_code=500)

@users_bp.route('/profile', methods=['PUT'])
@active_user_required
def update_profile(current_user):
    """更新使用者個人資料"""
    data, json_errors = safe_get_json()
    if json_errors:
        return error_response('JSON 格式錯誤', json_errors)
    
    try:
        # 更新允許的欄位
        if 'username' in data:
            username = data['username'].strip()
            if username != current_user.username:
                # 檢查新使用者名稱是否已存在
                if User.query.filter_by(username=username).first():
                    return error_response('使用者名稱已存在')
                current_user.username = username
        
        if 'profile_image' in data:
            current_user.profile_image = data['profile_image']
        
        db.session.commit()
        
        return success_response(current_user.to_dict(include_sensitive=True), '個人資料更新成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新個人資料失敗: {str(e)}', status_code=500)

@users_bp.route('/stats', methods=['GET'])
@active_user_required
def get_stats(current_user):
    """取得使用者統計資料"""
    try:
        stats = current_user.get_stats()
        return success_response(stats)
        
    except Exception as e:
        return error_response(f'取得統計資料失敗: {str(e)}', status_code=500)