from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey

# 從主 models 模組引入 db 實例
from . import db

class Amulet(db.Model):
    """平安符模型"""
    __tablename__ = 'amulets'
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    uid = Column(String(50), unique=True, nullable=False, index=True)  # NFC UID
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯（使用字串避免循環引入）
    checkins = db.relationship('Checkin', backref='amulet', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, id, user_id, uid, name, description=None):
        self.id = id
        self.user_id = user_id
        self.uid = uid
        self.name = name
        self.description = description
    
    def get_checkin_count(self):
        """取得打卡次數"""
        from .checkin import Checkin
        return db.session.query(db.func.count(Checkin.id)).filter(
            Checkin.amulet_id == self.id
        ).scalar() or 0
    
    def get_last_checkin(self):
        """取得最後打卡時間"""
        from .checkin import Checkin
        last_checkin = db.session.query(Checkin).filter(
            Checkin.amulet_id == self.id
        ).order_by(Checkin.checkin_time.desc()).first()
        return last_checkin.checkin_time if last_checkin else None
    
    def get_visited_temples(self):
        """取得造訪過的廟宇列表"""
        from .temple import Temple
        from .checkin import Checkin
        return db.session.query(Temple).join(
            Checkin, Temple.id == Checkin.temple_id
        ).filter(
            Checkin.amulet_id == self.id
        ).distinct().all()
    
    def to_dict(self, include_stats=False):
        """轉換為字典"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'uid': self.uid,
            'name': self.name,
            'description': self.description,
            'image_url': self.image_url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_stats:
            data['stats'] = {
                'checkin_count': self.get_checkin_count(),
                'last_checkin': self.get_last_checkin().isoformat() if self.get_last_checkin() else None,
                'visited_temples_count': len(self.get_visited_temples()),
            }
        
        return data
    
    @staticmethod
    def generate_default_name(user_username):
        """生成預設平安符名稱"""
        return f"{user_username}的平安符"
    
    def __repr__(self):
        return f'<Amulet {self.name} ({self.uid})>'