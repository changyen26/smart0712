from datetime import datetime, timedelta
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON

# 從主 models 模組引入 db 實例
from . import db

class Checkin(db.Model):
    """打卡記錄模型"""
    __tablename__ = 'checkins'
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    temple_id = Column(String(36), ForeignKey('temples.id'), nullable=False, index=True)
    amulet_id = Column(String(36), ForeignKey('amulets.id'), nullable=False, index=True)
    points_earned = Column(Integer, nullable=False)
    checkin_time = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    notes = Column(Text, nullable=True)
    extra_data = Column(JSON, nullable=True)  # 額外資料，如GPS位置等
    
    def __init__(self, id, user_id, temple_id, amulet_id, points_earned, notes=None, extra_data=None):
        self.id = id
        self.user_id = user_id
        self.temple_id = temple_id
        self.amulet_id = amulet_id
        self.points_earned = points_earned
        self.notes = notes
        self.extra_data = extra_data or {}
    
    @staticmethod
    def can_checkin(user_id, temple_id, hours_limit=24):
        """檢查是否可以在該廟宇打卡（避免重複打卡）"""
        time_limit = datetime.utcnow() - timedelta(hours=hours_limit)
        
        recent_checkin = Checkin.query.filter(
            Checkin.user_id == user_id,
            Checkin.temple_id == temple_id,
            Checkin.checkin_time >= time_limit
        ).first()
        
        return recent_checkin is None
    
    @staticmethod
    def get_user_stats(user_id):
        """取得使用者打卡統計"""
        from sqlalchemy import func, distinct
        
        stats = db.session.query(
            func.count(Checkin.id).label('total_checkins'),
            func.sum(Checkin.points_earned).label('total_points'),
            func.count(distinct(Checkin.temple_id)).label('unique_temples'),
            func.max(Checkin.checkin_time).label('last_checkin')
        ).filter(Checkin.user_id == user_id).first()
        
        return {
            'total_checkins': stats.total_checkins or 0,
            'total_points': stats.total_points or 0,
            'unique_temples': stats.unique_temples or 0,
            'last_checkin': stats.last_checkin.isoformat() if stats.last_checkin else None,
        }
    
    @staticmethod
    def get_streak_days(user_id):
        """計算連續打卡天數"""
        from sqlalchemy import func
        
        # 取得使用者所有打卡日期（去重）
        checkin_dates = db.session.query(
            func.date(Checkin.checkin_time).label('date')
        ).filter(
            Checkin.user_id == user_id
        ).distinct().order_by(
            func.date(Checkin.checkin_time).desc()
        ).all()
        
        if not checkin_dates:
            return 0
        
        # 計算連續天數
        streak = 0
        current_date = datetime.utcnow().date()
        
        for checkin_date in checkin_dates:
            date = checkin_date.date
            
            # 如果是今天或昨天，開始計算連續天數
            if date == current_date or date == current_date - timedelta(days=1):
                if date == current_date - timedelta(days=streak):
                    streak += 1
                    current_date = date
                else:
                    break
            else:
                break
        
        return streak
    
    @staticmethod
    def get_temple_ranking():
        """取得廟宇打卡排行榜"""
        from sqlalchemy import func
        from .temple import Temple
        
        return db.session.query(
            Temple.id,
            Temple.name,
            Temple.main_deity,
            func.count(Checkin.id).label('checkin_count'),
            func.count(func.distinct(Checkin.user_id)).label('unique_visitors')
        ).join(
            Checkin, Temple.id == Checkin.temple_id
        ).group_by(
            Temple.id, Temple.name, Temple.main_deity
        ).order_by(
            func.count(Checkin.id).desc()
        ).limit(10).all()
    
    @staticmethod
    def get_daily_stats(days=7):
        """取得每日打卡統計"""
        from sqlalchemy import func
        
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days-1)
        
        stats = db.session.query(
            func.date(Checkin.checkin_time).label('date'),
            func.count(Checkin.id).label('checkin_count'),
            func.count(func.distinct(Checkin.user_id)).label('unique_users')
        ).filter(
            func.date(Checkin.checkin_time) >= start_date,
            func.date(Checkin.checkin_time) <= end_date
        ).group_by(
            func.date(Checkin.checkin_time)
        ).order_by(
            func.date(Checkin.checkin_time)
        ).all()
        
        return [{
            'date': stat.date.isoformat(),
            'checkin_count': stat.checkin_count,
            'unique_users': stat.unique_users
        } for stat in stats]
    
    def to_dict(self, include_relations=False):
        """轉換為字典"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'temple_id': self.temple_id,
            'amulet_id': self.amulet_id,
            'points_earned': self.points_earned,
            'checkin_time': self.checkin_time.isoformat(),
            'notes': self.notes,
            'extra_data': self.extra_data or {},
        }
        
        if include_relations:
            # 動態引入避免循環引入
            user = db.session.get(db.registry._class_registry['User'], self.user_id)
            temple = db.session.get(db.registry._class_registry['Temple'], self.temple_id)
            amulet = db.session.get(db.registry._class_registry['Amulet'], self.amulet_id)
            
            data['user'] = user.to_dict() if user else None
            data['temple'] = temple.to_dict() if temple else None
            data['amulet'] = amulet.to_dict() if amulet else None
        
        return data
    
    def __repr__(self):
        return f'<Checkin {self.user_id} at {self.temple_id}>'