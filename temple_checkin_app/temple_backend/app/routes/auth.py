from flask import Blueprint, request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from app.models import db, User, Amulet
from app.utils.helpers import success_response, error_response, safe_get_json, generate_uuid, generate_amulet_uid
from app.utils.validators import validate_username, validate_email_format, validate_password

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# 用於儲存撤銷的 token（實際應用中應使用 Redis）
revoked_tokens = set()

@auth_bp.route('/register', methods=['POST'])
def register():
    """使用者註冊"""
    data, json_errors = safe_get_json()
    if json_errors:
        return error_response('JSON 格式錯誤', json_errors)
    
    # 驗證必填欄位
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data or not data[field]:
            return error_response(f'{field} 為必填欄位')
    
    username = data['username'].strip()
    email = data['email'].strip()
    password = data['password']
    
    # 驗證使用者名稱
    username_errors = validate_username(username)
    if username_errors:
        return error_response('使用者名稱格式不正確', username_errors)
    
    # 驗證電子郵件
    email_errors, validated_email = validate_email_format(email)
    if email_errors:
        return error_response('電子郵件格式不正確', email_errors)
    
    # 驗證密碼
    password_errors = validate_password(password)
    if password_errors:
        return error_response('密碼格式不正確', password_errors)
    
    # 檢查使用者名稱是否已存在
    if User.query.filter_by(username=username).first():
        return error_response('使用者名稱已存在')
    
    # 檢查電子郵件是否已存在
    if User.query.filter_by(email=validated_email).first():
        return error_response('電子郵件已被註冊')
    
    try:
        # 只建立新使用者，不創建平安符
        user_id = generate_uuid()
        user = User(
            id=user_id,
            username=username,
            email=validated_email,
            password=password
        )
        
        db.session.add(user)
        db.session.commit()
        
        # 生成 JWT token
        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)
        
        response_data = {
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token,
            'message': '註冊成功，請拿到實體平安符後進行綁定'
        }
        
        return success_response(response_data, '註冊成功', 201)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'註冊失敗: {str(e)}', status_code=500)

@auth_bp.route('/bind-amulet', methods=['POST'])
@jwt_required()
def bind_amulet():
    """綁定平安符"""
    data, json_errors = safe_get_json()
    if json_errors:
        return error_response('JSON 格式錯誤', json_errors)
    
    # 獲取當前用戶
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return error_response('用戶不存在', status_code=404)
    
    # 驗證必填欄位
    if 'amulet_uid' not in data or not data['amulet_uid']:
        return error_response('平安符 UID 為必填欄位')
    
    amulet_uid = data['amulet_uid'].strip().upper()
    
    try:
        # 檢查平安符 UID 是否已被綁定
        existing_amulet = Amulet.query.filter_by(uid=amulet_uid).first()
        if existing_amulet:
            return error_response('此平安符已被綁定')
        
        # 創建新的平安符綁定
        amulet_id = generate_uuid()
        amulet = Amulet(
            id=amulet_id,
            user_id=current_user_id,
            uid=amulet_uid,
            name=data.get('name', f"{user.username}的平安符"),
            description=data.get('description', '用戶綁定的平安符')
        )
        
        db.session.add(amulet)
        db.session.commit()
        
        response_data = {
            'amulet': amulet.to_dict(),
            'message': '平安符綁定成功'
        }
        
        return success_response(response_data, '平安符綁定成功', 201)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'綁定失敗: {str(e)}', status_code=500)

@auth_bp.route('/unbind-amulet/<amulet_id>', methods=['DELETE'])
@jwt_required()
def unbind_amulet(amulet_id):
    """解綁平安符"""
    try:
        current_user_id = get_jwt_identity()
        
        # 查找平安符
        amulet = Amulet.query.filter_by(id=amulet_id, user_id=current_user_id).first()
        if not amulet:
            return error_response('平安符不存在或不屬於當前用戶', status_code=404)
        
        # 軟刪除（設為不活躍）而不是真正刪除
        amulet.is_active = False
        db.session.commit()
        
        return success_response(message='平安符解綁成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'解綁失敗: {str(e)}', status_code=500)

@auth_bp.route('/login', methods=['POST'])
def login():
    """使用者登入"""
    data, json_errors = safe_get_json()
    if json_errors:
        return error_response('JSON 格式錯誤', json_errors)
    
    # 驗證必填欄位
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not email or not password:
        return error_response('電子郵件和密碼為必填欄位')
    
    # 尋找使用者
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return error_response('電子郵件或密碼錯誤', status_code=401)
    
    if not user.is_active:
        return error_response('帳戶已被停用', status_code=403)
    
    try:
        # 生成 JWT token
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        # 取得使用者的平安符
        amulets = Amulet.query.filter_by(user_id=user.id, is_active=True).all()
        
        response_data = {
            'user': user.to_dict(include_sensitive=True),
            'amulets': [amulet.to_dict() for amulet in amulets],
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        
        return success_response(response_data, '登入成功')
        
    except Exception as e:
        return error_response(f'登入失敗: {str(e)}', status_code=500)

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新 access token"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return error_response('使用者不存在或已被停用', status_code=404)
        
        new_access_token = create_access_token(identity=current_user_id)
        
        response_data = {
            'access_token': new_access_token
        }
        
        return success_response(response_data, 'Token 刷新成功')
        
    except Exception as e:
        return error_response(f'Token 刷新失敗: {str(e)}', status_code=500)

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """使用者登出"""
    try:
        # 將 token 加入撤銷清單
        jti = get_jwt()['jti']
        revoked_tokens.add(jti)
        
        return success_response(message='登出成功')
        
    except Exception as e:
        return error_response(f'登出失敗: {str(e)}', status_code=500)

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """取得當前使用者資訊"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return error_response('使用者不存在', status_code=404)
        
        # 取得使用者的平安符
        amulets = Amulet.query.filter_by(user_id=user.id, is_active=True).all()
        
        response_data = {
            'user': user.to_dict(include_sensitive=True),
            'amulets': [amulet.to_dict(include_stats=True) for amulet in amulets]
        }
        
        return success_response(response_data)
        
    except Exception as e:
        return error_response(f'取得使用者資訊失敗: {str(e)}', status_code=500)

# JWT token 檢查器
@auth_bp.before_app_request
def check_if_token_revoked():
    """檢查 token 是否已被撤銷"""
    try:
        jti = get_jwt()['jti']
        if jti in revoked_tokens:
            return error_response('Token 已失效', status_code=401)
    except:
        pass