import re
from email_validator import validate_email, EmailNotValidError

def validate_username(username):
    """驗證使用者名稱"""
    errors = []
    
    if not username:
        errors.append('使用者名稱不能為空')
        return errors
    
    if len(username) < 3:
        errors.append('使用者名稱至少需要3個字元')
    
    if len(username) > 20:
        errors.append('使用者名稱不能超過20個字元')
    
    if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fff]+$', username):
        errors.append('使用者名稱只能包含字母、數字、底線和中文字元')
    
    return errors

def validate_email_format(email):
    """驗證電子郵件格式"""
    try:
        validated_email = validate_email(email)
        return [], validated_email.email
    except EmailNotValidError as e:
        return [str(e)], None

def validate_password(password):
    """驗證密碼強度"""
    errors = []
    
    if not password:
        errors.append('密碼不能為空')
        return errors
    
    if len(password) < 6:
        errors.append('密碼至少需要6個字元')
    
    if len(password) > 20:
        errors.append('密碼不能超過20個字元')
    
    # 可以添加更多密碼複雜度要求
    # if not re.search(r'[A-Z]', password):
    #     errors.append('密碼必須包含至少一個大寫字母')
    
    # if not re.search(r'[a-z]', password):
    #     errors.append('密碼必須包含至少一個小寫字母')
    
    # if not re.search(r'\d', password):
    #     errors.append('密碼必須包含至少一個數字')
    
    return errors

def validate_temple_data(data):
    """驗證廟宇資料"""
    errors = []
    required_fields = ['name', 'main_deity', 'description', 'address', 'latitude', 'longitude']
    
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f'{field} 為必填欄位')
    
    # 驗證座標
    try:
        lat = float(data.get('latitude', 0))
        lng = float(data.get('longitude', 0))
        
        if not (-90 <= lat <= 90):
            errors.append('緯度必須在 -90 到 90 之間')
        
        if not (-180 <= lng <= 180):
            errors.append('經度必須在 -180 到 180 之間')
    except (ValueError, TypeError):
        errors.append('座標格式不正確')
    
    # 驗證福報加成值
    try:
        blessing_bonus = int(data.get('blessing_bonus', 1))
        if blessing_bonus < 1 or blessing_bonus > 10:
            errors.append('福報加成值必須在 1 到 10 之間')
    except (ValueError, TypeError):
        errors.append('福報加成值必須為整數')
    
    return errors

def validate_amulet_data(data):
    """驗證平安符資料"""
    errors = []
    
    if 'name' not in data or not data['name'].strip():
        errors.append('平安符名稱不能為空')
    elif len(data['name']) > 100:
        errors.append('平安符名稱不能超過100個字元')
    
    if 'uid' not in data or not data['uid'].strip():
        errors.append('UID 不能為空')
    elif len(data['uid']) > 50:
        errors.append('UID 不能超過50個字元')
    
    return errors

def validate_checkin_data(data):
    """驗證打卡資料"""
    errors = []
    required_fields = ['temple_id', 'amulet_uid']
    
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f'{field} 為必填欄位')
    
    return errors

def validate_pagination_params(page, per_page, max_per_page=100):
    """驗證分頁參數"""
    errors = []
    
    try:
        page = int(page) if page else 1
        if page < 1:
            errors.append('頁碼必須大於 0')
    except ValueError:
        errors.append('頁碼格式不正確')
        page = 1
    
    try:
        per_page = int(per_page) if per_page else 20
        if per_page < 1:
            errors.append('每頁數量必須大於 0')
        elif per_page > max_per_page:
            errors.append(f'每頁數量不能超過 {max_per_page}')
    except ValueError:
        errors.append('每頁數量格式不正確')
        per_page = 20
    
    return errors, page, per_page