from flask import Blueprint
from app.models import db, Amulet
from app.utils.helpers import success_response, error_response, safe_get_json, generate_uuid, generate_amulet_uid
from app.utils.auth import active_user_required
from app.utils.validators import validate_amulet_data

amulets_bp = Blueprint('amulets', __name__, url_prefix='/api/amulets')

@amulets_bp.route('', methods=['GET'])
@active_user_required
def get_amulets(current_user):
    """取得使用者的平安符列表"""
    try:
        amulets = current_user.amulets.filter_by(is_active=True).all()
        amulets_data = [amulet.to_dict(include_stats=True) for amulet in amulets]
        
        return success_response(amulets_data)
        
    except Exception as e:
        return error_response(f'取得平安符列表失敗: {str(e)}', status_code=500)

@amulets_bp.route('', methods=['POST'])
@active_user_required
def create_amulet(current_user):
    """建立新的平安符"""
    data, json_errors = safe_get_json()
    if json_errors:
        return error_response('JSON 格式錯誤', json_errors)
    
    # 驗證資料
    validation_errors = validate_amulet_data(data)
    if validation_errors:
        return error_response('資料驗證失敗', validation_errors)
    
    name = data['name'].strip()
    description = data.get('description', '').strip()
    uid = data.get('uid', generate_amulet_uid()).strip()
    
    try:
        # 檢查 UID 是否已存在
        if Amulet.query.filter_by(uid=uid).first():
            return error_response('此 UID 已被使用')
        
        # 建立平安符
        amulet_id = generate_uuid()
        amulet = Amulet(
            id=amulet_id,
            user_id=current_user.id,
            uid=uid,
            name=name,
            description=description
        )
        
        if 'image_url' in data:
            amulet.image_url = data['image_url']
        
        db.session.add(amulet)
        db.session.commit()
        
        return success_response(amulet.to_dict(), '平安符建立成功', 201)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'建立平安符失敗: {str(e)}', status_code=500)

@amulets_bp.route('/<amulet_id>', methods=['PUT'])
@active_user_required
def update_amulet(current_user, amulet_id):
    """更新平安符資訊"""
    data, json_errors = safe_get_json()
    if json_errors:
        return error_response('JSON 格式錯誤', json_errors)
    
    try:
        amulet = Amulet.query.filter_by(id=amulet_id, user_id=current_user.id).first()
        
        if not amulet:
            return error_response('平安符不存在', status_code=404)
        
        # 更新允許的欄位
        if 'name' in data:
            name = data['name'].strip()
            if not name:
                return error_response('平安符名稱不能為空')
            amulet.name = name
        
        if 'description' in data:
            amulet.description = data['description'].strip()
        
        if 'image_url' in data:
            amulet.image_url = data['image_url']
        
        db.session.commit()
        
        return success_response(amulet.to_dict(), '平安符更新成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新平安符失敗: {str(e)}', status_code=500)

@amulets_bp.route('/<amulet_id>', methods=['DELETE'])
@active_user_required
def delete_amulet(current_user, amulet_id):
    """刪除平安符（軟刪除）"""
    try:
        amulet = Amulet.query.filter_by(id=amulet_id, user_id=current_user.id).first()
        
        if not amulet:
            return error_response('平安符不存在', status_code=404)
        
        # 軟刪除
        amulet.is_active = False
        db.session.commit()
        
        return success_response(message='平安符刪除成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'刪除平安符失敗: {str(e)}', status_code=500)