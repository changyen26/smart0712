# 路由模組初始化檔案
from .auth import auth_bp
from .users import users_bp
from .temples import temples_bp
from .checkin import checkin_bp
from .amulets import amulets_bp
from .admin import admin_bp

__all__ = [
    'auth_bp',
    'users_bp', 
    'temples_bp',
    'checkin_bp',
    'amulets_bp',
    'admin_bp'
]