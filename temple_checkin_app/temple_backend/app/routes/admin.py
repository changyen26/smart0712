from flask import Blueprint, request
from app.models import db, Temple, Checkin, User
from app.utils.helpers import success_response, error_response, safe_get_json, generate_uuid, paginate_response
from app.utils.auth import admin_required
from app.utils.validators import validate_temple_data, validate_pagination_params

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/temples', methods=['GET'])
@admin_required
def get_all_temples():
    """取得所有廟宇（包含停用的）"""
    try:
        page = request.args.get('page', 1)
        per_page = request.args.get('per_page', 20)
        search = request.args.get('search', '')
        status = request.args.get('status', 'all')  # all, active, inactive
        
        errors, page, per_page = validate_pagination_params(page, per_page)
        if errors:
            return error_response('分頁參數錯誤', errors)
        
        query = Temple.query
        
        # 狀態篩選
        if status == 'active':
            query = query.filter(Temple.is_active == True)
        elif status == 'inactive':
            query = query.filter(Temple.is_active == False)
        
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

@admin_bp.route('/temples', methods=['POST'])
@admin_required
def create_temple():
    """建立新廟宇"""
    data, json_errors = safe_get_json()
    if json_errors:
        return error_response('JSON 格式錯誤', json_errors)
    
    # 驗證資料
    validation_errors = validate_temple_data(data)
    if validation_errors:
        return error_response('資料驗證失敗', validation_errors)
    
    try:
        temple_id = generate_uuid()
        temple = Temple(
            id=temple_id,
            name=data['name'].strip(),
            main_deity=data['main_deity'].strip(),
            description=data['description'].strip(),
            address=data['address'].strip(),
            latitude=float(data['latitude']),
            longitude=float(data['longitude']),
            blessing_bonus=int(data.get('blessing_bonus', 1))
        )
        
        # 可選欄位
        if 'phone' in data:
            temple.phone = data['phone'].strip()
        if 'website' in data:
            temple.website = data['website'].strip()
        if 'opening_hours' in data:
            temple.opening_hours = data['opening_hours'].strip()
        if 'image_url' in data:
            temple.image_url = data['image_url'].strip()
        
        db.session.add(temple)
        db.session.commit()
        
        return success_response(temple.to_dict(), '廟宇建立成功', 201)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'建立廟宇失敗: {str(e)}', status_code=500)

@admin_bp.route('/temples/<temple_id>', methods=['PUT'])
@admin_required
def update_temple(temple_id):
    """更新廟宇資訊"""
    data, json_errors = safe_get_json()
    if json_errors:
        return error_response('JSON 格式錯誤', json_errors)
    
    try:
        temple = Temple.query.get(temple_id)
        if not temple:
            return error_response('廟宇不存在', status_code=404)
        
        # 更新允許的欄位
        if 'name' in data:
            temple.name = data['name'].strip()
        if 'main_deity' in data:
            temple.main_deity = data['main_deity'].strip()
        if 'description' in data:
            temple.description = data['description'].strip()
        if 'address' in data:
            temple.address = data['address'].strip()
        if 'latitude' in data:
            temple.latitude = float(data['latitude'])
        if 'longitude' in data:
            temple.longitude = float(data['longitude'])
        if 'blessing_bonus' in data:
            temple.blessing_bonus = int(data['blessing_bonus'])
        if 'phone' in data:
            temple.phone = data['phone'].strip()
        if 'website' in data:
            temple.website = data['website'].strip()
        if 'opening_hours' in data:
            temple.opening_hours = data['opening_hours'].strip()
        if 'image_url' in data:
            temple.image_url = data['image_url'].strip()
        if 'is_active' in data:
            temple.is_active = bool(data['is_active'])
        
        db.session.commit()
        
        return success_response(temple.to_dict(), '廟宇更新成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新廟宇失敗: {str(e)}', status_code=500)

@admin_bp.route('/temples/<temple_id>', methods=['DELETE'])
@admin_required
def delete_temple(temple_id):
    """刪除廟宇（軟刪除）"""
    try:
        temple = Temple.query.get(temple_id)
        if not temple:
            return error_response('廟宇不存在', status_code=404)
        
        temple.is_active = False
        db.session.commit()
        
        return success_response(message='廟宇刪除成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'刪除廟宇失敗: {str(e)}', status_code=500)

@admin_bp.route('/stats', methods=['GET'])
@admin_required
def get_admin_stats():
    """取得管理員統計資料"""
    try:
        # 基本統計
        total_users = User.query.filter_by(is_active=True).count()
        total_temples = Temple.query.filter_by(is_active=True).count()
        total_checkins = Checkin.query.count()
        
        # 最近7天的打卡統計
        daily_stats = Checkin.get_daily_stats(7)
        
        # 廟宇排行榜
        temple_ranking = Checkin.get_temple_ranking()
        
        stats_data = {
            'overview': {
                'total_users': total_users,
                'total_temples': total_temples,
                'total_checkins': total_checkins,
            },
            'daily_stats': daily_stats,
            'temple_ranking': [
                {
                    'temple_id': rank.id,
                    'temple_name': rank.name,
                    'main_deity': rank.main_deity,
                    'checkin_count': rank.checkin_count,
                    'unique_visitors': rank.unique_visitors
                }
                for rank in temple_ranking
            ]
        }
        
        return success_response(stats_data)
        
    except Exception as e:
        return error_response(f'取得統計資料失敗: {str(e)}', status_code=500)

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    """取得所有使用者列表"""
    try:
        page = request.args.get('page', 1)
        per_page = request.args.get('per_page', 20)
        search = request.args.get('search', '')
        
        errors, page, per_page = validate_pagination_params(page, per_page)
        if errors:
            return error_response('分頁參數錯誤', errors)
        
        query = User.query
        
        # 搜尋功能
        if search:
            search_term = f'%{search}%'
            query = query.filter(
                db.or_(
                    User.username.like(search_term),
                    User.email.like(search_term)
                )
            )
        
        query = query.order_by(User.created_at.desc())
        
        return paginate_response(query, page, per_page)
        
    except Exception as e:
        return error_response(f'取得使用者列表失敗: {str(e)}', status_code=500)

@admin_bp.route('/users/<user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """切換使用者啟用狀態"""
    try:
        user = User.query.get(user_id)
        if not user:
            return error_response('使用者不存在', status_code=404)
        
        user.is_active = not user.is_active
        db.session.commit()
        
        status = '啟用' if user.is_active else '停用'
        return success_response(user.to_dict(), f'使用者已{status}')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'切換使用者狀態失敗: {str(e)}', status_code=500)