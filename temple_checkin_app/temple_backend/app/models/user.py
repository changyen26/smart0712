from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean

# 從主 models 模組引入 db 實例
from . import db

class User(db.Model):
    """使用者模型"""
    __tablename__ = 'users'
    
    id = Column(String(36), primary_key=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    blessing_points = Column(Integer, default=0, nullable=False)
    profile_image = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯（使用字串避免循環引入）
    amulets = db.relationship('Amulet', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    checkins = db.relationship('Checkin', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, id, username, email, password=None):
        self.id = id
        self.username = username
        self.email = email
        if password:
            self.set_password(password)
    
    def set_password(self, password):
        """設定密碼雜湊"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """驗證密碼"""
        return check_password_hash(self.password_hash, password)
    
    def add_blessing_points(self, points):
        """增加福報值"""
        self.blessing_points += points
        self.updated_at = datetime.utcnow()
    
    def get_blessing_level(self):
        """取得福報等級"""
        levels = [
            {'level': 1, 'name': '初心者', 'min_points': 0, 'max_points': 99},
            {'level': 2, 'name': '虔誠信徒', 'min_points': 100, 'max_points': 499},
            {'level': 3, 'name': '福報滿滿', 'min_points': 500, 'max_points': 1499},
            {'level': 4, 'name': '功德圓滿', 'min_points': 1500, 'max_points': 4999},
            {'level': 5, 'name': '大德高僧', 'min_points': 5000, 'max_points': 9999},
            {'level': 6, 'name': '神通廣大', 'min_points': 10000, 'max_points': -1},
        ]
        
        for level in levels:
            if level['max_points'] == -1 or self.blessing_points <= level['max_points']:
                return level
        return levels[-1]
    
    def get_stats(self):
        """取得使用者統計資料"""
        # 動態引入避免循環引入
        from .checkin import Checkin
        
        total_temples = db.session.query(
            db.func.count(db.distinct(Checkin.temple_id))
        ).filter(Checkin.user_id == self.id).scalar() or 0
        
        total_checkins = db.session.query(
            db.func.count(Checkin.id)
        ).filter(Checkin.user_id == self.id).scalar() or 0
        
        return {
            'total_checkins': total_checkins,
            'total_temples': total_temples,
            'blessing_points': self.blessing_points,
            'blessing_level': self.get_blessing_level(),
            'join_date': self.created_at.strftime('%Y-%m-%d'),
        }
    
    def to_dict(self, include_sensitive=False):
        """轉換為字典"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'blessing_points': self.blessing_points,
            'profile_image': self.profile_image,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_sensitive:
            data['is_admin'] = self.is_admin
            data['stats'] = self.get_stats()
        
        return data
    
    def __repr__(self):
        return f'<User {self.username}>'