from flask import Blueprint, request
from app.models import db, Checkin, Temple, Amulet, User
from app.utils.helpers import success_response, error_response, safe_get_json, generate_uuid, calculate_points
from app.utils.auth import active_user_required
from app.utils.validators import validate_checkin_data

checkin_bp = Blueprint('checkin', __name__, url_prefix='/api/checkin')

@checkin_bp.route('', methods=['POST'])
@active_user_required
def create_checkin(current_user):
    """建立打卡記錄"""
    data, json_errors = safe_get_json()
    if json_errors:
        return error_response('JSON 格式錯誤', json_errors)
    
    # 驗證資料
    validation_errors = validate_checkin_data(data)
    if validation_errors:
        return error_response('資料驗證失敗', validation_errors)
    
    temple_id = data['temple_id']
    amulet_uid = data['amulet_uid']
    notes = data.get('notes', '')
    extra_data = data.get('extra_data', {})  # 改為 extra_data
    
    try:
        # 檢查廟宇是否存在
        temple = Temple.query.get(temple_id)
        if not temple or not temple.is_active:
            return error_response('廟宇不存在或已停用', status_code=404)
        
        # 檢查平安符是否存在且屬於當前使用者
        amulet = Amulet.query.filter_by(uid=amulet_uid, user_id=current_user.id, is_active=True).first()
        if not amulet:
            return error_response('平安符不存在或不屬於您', status_code=404)
        
        # 檢查是否可以打卡（避免重複打卡）
        if not Checkin.can_checkin(current_user.id, temple_id):
            return error_response('您在24小時內已在此廟宇打卡過了', status_code=400)
        
        # 計算獲得的福報值
        base_points = 1
        points_earned = calculate_points(base_points, temple.blessing_bonus)
        
        # 建立打卡記錄
        checkin_id = generate_uuid()
        checkin = Checkin(
            id=checkin_id,
            user_id=current_user.id,
            temple_id=temple_id,
            amulet_id=amulet.id,
            points_earned=points_earned,
            notes=notes,
            extra_data=extra_data  # 改為 extra_data
        )
        
        # 更新使用者福報值
        current_user.add_blessing_points(points_earned)
        
        db.session.add(checkin)
        db.session.commit()
        
        response_data = {
            'checkin': checkin.to_dict(include_relations=True),
            'points_earned': points_earned,
            'total_blessing_points': current_user.blessing_points,
            'blessing_level': current_user.get_blessing_level()
        }
        
        return success_response(response_data, '打卡成功！', 201)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'打卡失敗: {str(e)}', status_code=500)

@checkin_bp.route('/history', methods=['GET'])
@active_user_required
def get_checkin_history(current_user):
    """取得打卡歷史記錄"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = Checkin.query.filter_by(user_id=current_user.id).order_by(Checkin.checkin_time.desc())
        
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        checkins_data = []
        for checkin in paginated.items:
            checkin_dict = checkin.to_dict(include_relations=True)
            checkins_data.append(checkin_dict)
        
        response_data = {
            'checkins': checkins_data,
            'pagination': {
                'page': paginated.page,
                'per_page': paginated.per_page,
                'total': paginated.total,
                'pages': paginated.pages,
                'has_prev': paginated.has_prev,
                'has_next': paginated.has_next,
            }
        }
        
        return success_response(response_data)
        
    except Exception as e:
        return error_response(f'取得打卡歷史失敗: {str(e)}', status_code=500)

@checkin_bp.route('/stats', methods=['GET'])
@active_user_required
def get_checkin_stats(current_user):
    """取得打卡統計資料"""
    try:
        stats = Checkin.get_user_stats(current_user.id)
        streak_days = Checkin.get_streak_days(current_user.id)
        
        stats['streak_days'] = streak_days
        stats['blessing_level'] = current_user.get_blessing_level()
        
        return success_response(stats)
        
    except Exception as e:
        return error_response(f'取得統計資料失敗: {str(e)}', status_code=500)