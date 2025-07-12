from flask import Blueprint, request
from app.models import db, Temple
from app.utils.helpers import success_response, error_response, paginate_response
from app.utils.validators import validate_pagination_params

temples_bp = Blueprint('temples', __name__, url_prefix='/api/temples')

@temples_bp.route('', methods=['GET'])
def get_temples():
    """取得廟宇列表"""
    try:
        page = request.args.get('page', 1)
        per_page = request.args.get('per_page', 20)
        search = request.args.get('search', '')
        
        errors, page, per_page = validate_pagination_params(page, per_page)
        if errors:
            return error_response('分頁參數錯誤', errors)
        
        query = Temple.query.filter(Temple.is_active == True)
        
        # 搜尋功能
        if search:
            search_term = f'%{search}%'
            query = query.filter(
                db.or_(
                    Temple.name.like(search_term),
                    Temple.main_deity.like(search_term),
                    Temple.address.like(search_term)
                )
            )
        
        query = query.order_by(Temple.created_at.desc())
        
        return paginate_response(query, page, per_page)
        
    except Exception as e:
        return error_response(f'取得廟宇列表失敗: {str(e)}', status_code=500)

@temples_bp.route('/<temple_id>', methods=['GET'])
def get_temple(temple_id):
    """取得單一廟宇詳細資訊"""
    try:
        temple = Temple.query.get(temple_id)
        
        if not temple or not temple.is_active:
            return error_response('廟宇不存在', status_code=404)
        
        # 檢查是否提供使用者位置
        user_lat = request.args.get('lat')
        user_lng = request.args.get('lng')
        user_location = None
        
        if user_lat and user_lng:
            try:
                user_location = (float(user_lat), float(user_lng))
            except ValueError:
                pass
        
        temple_data = temple.to_dict(include_stats=True, user_location=user_location)
        
        return success_response(temple_data)
        
    except Exception as e:
        return error_response(f'取得廟宇資訊失敗: {str(e)}', status_code=500)

@temples_bp.route('/nearby', methods=['GET'])
def get_nearby_temples():
    """取得附近的廟宇"""
    try:
        lat = request.args.get('lat')
        lng = request.args.get('lng')
        radius = request.args.get('radius', 5)  # 預設5公里
        limit = request.args.get('limit', 20)
        
        if not lat or not lng:
            return error_response('需要提供座標參數 (lat, lng)')
        
        try:
            latitude = float(lat)
            longitude = float(lng)
            radius_km = float(radius)
            limit_count = int(limit)
        except ValueError:
            return error_response('座標格式不正確')
        
        nearby_temples = Temple.find_nearby(latitude, longitude, radius_km, limit_count)
        
        temples_data = []
        for temple, distance in nearby_temples:
            temple_dict = temple.to_dict()
            temple_dict['distance'] = round(distance, 2)
            temples_data.append(temple_dict)
        
        return success_response(temples_data)
        
    except Exception as e:
        return error_response(f'搜尋附近廟宇失敗: {str(e)}', status_code=500)