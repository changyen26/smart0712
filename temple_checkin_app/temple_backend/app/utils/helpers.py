import uuid
import json
from datetime import datetime
from flask import jsonify

def generate_uuid():
    """生成 UUID"""
    return str(uuid.uuid4())

def success_response(data=None, message='成功', status_code=200):
    """成功回應格式"""
    response = {
        'success': True,
        'message': message,
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    }
    return jsonify(response), status_code

def error_response(message='發生錯誤', errors=None, status_code=400):
    """錯誤回應格式"""
    response = {
        'success': False,
        'message': message,
        'errors': errors or [],
        'timestamp': datetime.utcnow().isoformat()
    }
    return jsonify(response), status_code

def paginate_response(query, page, per_page, endpoint=None, **kwargs):
    """分頁回應格式"""
    try:
        paginated = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        items = [item.to_dict() if hasattr(item, 'to_dict') else item for item in paginated.items]
        
        response_data = {
            'items': items,
            'pagination': {
                'page': paginated.page,
                'per_page': paginated.per_page,
                'total': paginated.total,
                'pages': paginated.pages,
                'has_prev': paginated.has_prev,
                'prev_num': paginated.prev_num,
                'has_next': paginated.has_next,
                'next_num': paginated.next_num,
            }
        }
        
        return success_response(response_data)
    except Exception as e:
        return error_response(f'分頁查詢失敗: {str(e)}', status_code=500)

def safe_get_json():
    """安全取得 JSON 資料"""
    try:
        from flask import request
        data = request.get_json()
        if data is None:
            return {}, ['請求必須包含 JSON 資料']
        return data, []
    except Exception as e:
        return {}, [f'JSON 格式錯誤: {str(e)}']

def format_datetime(dt):
    """格式化日期時間"""
    if dt is None:
        return None
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def parse_datetime(date_string):
    """解析日期時間字串"""
    try:
        return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    except:
        return None

def calculate_points(base_points, bonus_multiplier=1, special_bonus=0):
    """計算福報值"""
    return int(base_points * bonus_multiplier) + special_bonus

def generate_amulet_uid():
    """生成平安符 UID（模擬 NFC UID）"""
    # 生成 8 字元的十六進位字串
    return uuid.uuid4().hex[:8].upper()

def is_valid_coordinates(latitude, longitude):
    """驗證座標是否有效"""
    try:
        lat = float(latitude)
        lng = float(longitude)
        return -90 <= lat <= 90 and -180 <= lng <= 180
    except (ValueError, TypeError):
        return False

def sanitize_filename(filename):
    """清理檔案名稱"""
    import re
    # 移除不安全的字元
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # 限制長度
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:255-len(ext)-1] + '.' + ext if ext else name[:255]
    return filename

def get_file_extension(filename):
    """取得檔案副檔名"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

def allowed_file(filename, allowed_extensions=None):
    """檢查檔案是否允許上傳"""
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    return '.' in filename and get_file_extension(filename) in allowed_extensions

class CustomJSONEncoder(json.JSONEncoder):
    """自定義 JSON 編碼器"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)