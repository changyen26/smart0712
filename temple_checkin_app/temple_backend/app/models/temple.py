from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, Float
import math

# 從主 models 模組引入 db 實例
from . import db

class Temple(db.Model):
    """廟宇模型"""
    __tablename__ = 'temples'
    
    id = Column(String(36), primary_key=True)
    name = Column(String(200), nullable=False, index=True)
    main_deity = Column(String(100), nullable=False)  # 主祀神
    description = Column(Text, nullable=True)
    address = Column(Text, nullable=False)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    image_url = Column(Text, nullable=True)
    blessing_bonus = Column(Integer, default=1, nullable=False)  # 福報加成值
    phone = Column(String(20), nullable=True)
    website = Column(Text, nullable=True)
    opening_hours = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯（使用字串避免循環引入）
    checkins = db.relationship('Checkin', backref='temple', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, id, name, main_deity, description, address, latitude, longitude, blessing_bonus=1):
        self.id = id
        self.name = name
        self.main_deity = main_deity
        self.description = description
        self.address = address
        self.latitude = latitude
        self.longitude = longitude
        self.blessing_bonus = blessing_bonus
    
    def get_checkin_count(self):
        """取得總打卡次數"""
        from .checkin import Checkin
        return db.session.query(db.func.count(Checkin.id)).filter(
            Checkin.temple_id == self.id
        ).scalar() or 0
    
    def get_unique_visitors_count(self):
        """取得獨特訪客數"""
        from .checkin import Checkin
        return db.session.query(
            db.func.count(db.distinct(Checkin.user_id))
        ).filter(Checkin.temple_id == self.id).scalar() or 0
    
    def get_recent_checkins(self, limit=10):
        """取得最近的打卡記錄"""
        from .checkin import Checkin
        return db.session.query(Checkin).filter(
            Checkin.temple_id == self.id
        ).order_by(Checkin.checkin_time.desc()).limit(limit).all()
    
    def calculate_distance(self, lat, lng):
        """計算與指定座標的距離（公里）"""
        # 使用 Haversine 公式計算距離
        R = 6371  # 地球半徑（公里）
        
        lat1_rad = math.radians(self.latitude)
        lng1_rad = math.radians(self.longitude)
        lat2_rad = math.radians(lat)
        lng2_rad = math.radians(lng)
        
        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad
        
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    @staticmethod
    def find_nearby(latitude, longitude, radius_km=5, limit=20):
        """尋找附近的廟宇"""
        # 簡化版本：使用邊界框篩選
        lat_delta = radius_km / 111.0  # 緯度每度約111公里
        lng_delta = radius_km / (111.0 * math.cos(math.radians(latitude)))
        
        temples = Temple.query.filter(
            Temple.is_active == True,
            Temple.latitude.between(latitude - lat_delta, latitude + lat_delta),
            Temple.longitude.between(longitude - lng_delta, longitude + lng_delta)
        ).all()
        
        # 計算精確距離並排序
        temple_distances = []
        for temple in temples:
            distance = temple.calculate_distance(latitude, longitude)
            if distance <= radius_km:
                temple_distances.append((temple, distance))
        
        # 按距離排序
        temple_distances.sort(key=lambda x: x[1])
        
        return temple_distances[:limit]
    
    def get_popular_times(self):
        """取得熱門時段統計"""
        from sqlalchemy import func
        from .checkin import Checkin
        
        # 按小時統計打卡次數
        result = db.session.query(
            func.extract('hour', Checkin.checkin_time).label('hour'),
            func.count(Checkin.id).label('count')
        ).filter(
            Checkin.temple_id == self.id
        ).group_by(
            func.extract('hour', Checkin.checkin_time)
        ).all()
        
        return {int(hour): count for hour, count in result}
    
    def to_dict(self, include_stats=False, user_location=None):
        """轉換為字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'main_deity': self.main_deity,
            'description': self.description,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'image_url': self.image_url,
            'blessing_bonus': self.blessing_bonus,
            'phone': self.phone,
            'website': self.website,
            'opening_hours': self.opening_hours,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_stats:
            data['stats'] = {
                'checkin_count': self.get_checkin_count(),
                'unique_visitors': self.get_unique_visitors_count(),
                'popular_times': self.get_popular_times(),
            }
        
        if user_location:
            lat, lng = user_location
            data['distance'] = round(self.calculate_distance(lat, lng), 2)
        
        return data
    
    def __repr__(self):
        return f'<Temple {self.name}>'#緯度每度約111公里
        lng_delta = radius_km / (111.0 * math.cos(math.radians(latitude)))
        
        temples = Temple.query.filter(
            Temple.is_active == True,
            Temple.latitude.between(latitude - lat_delta, latitude + lat_delta),
            Temple.longitude.between(longitude - lng_delta, longitude + lng_delta)
        ).all()
        
        # 計算精確距離並排序
        temple_distances = []
        for temple in temples:
            distance = temple.calculate_distance(latitude, longitude)
            if distance <= radius_km:
                temple_distances.append((temple, distance))
        
        # 按距離排序
        temple_distances.sort(key=lambda x: x[1])
        
        return temple_distances[:limit]
    
    def get_popular_times(self):
        """取得熱門時段統計"""
        from sqlalchemy import func
        from app.models.checkin import Checkin
        
        # 按小時統計打卡次數
        result = db.session.query(
            func.extract('hour', Checkin.checkin_time).label('hour'),
            func.count(Checkin.id).label('count')
        ).filter(
            Checkin.temple_id == self.id
        ).group_by(
            func.extract('hour', Checkin.checkin_time)
        ).all()
        
        return {int(hour): count for hour, count in result}
    
    def to_dict(self, include_stats=False, user_location=None):
        """轉換為字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'main_deity': self.main_deity,
            'description': self.description,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'image_url': self.image_url,
            'blessing_bonus': self.blessing_bonus,
            'phone': self.phone,
            'website': self.website,
            'opening_hours': self.opening_hours,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_stats:
            data['stats'] = {
                'checkin_count': self.get_checkin_count(),
                'unique_visitors': self.get_unique_visitors_count(),
                'popular_times': self.get_popular_times(),
            }
        
        if user_location:
            lat, lng = user_location
            data['distance'] = round(self.calculate_distance(lat, lng), 2)
        
        return data
    
    def __repr__(self):
        return f'<Temple {self.name}>'