from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 按順序匯入模型
from .user import User
from .temple import Temple  
from .amulet import Amulet
from .checkin import Checkin

__all__ = ['db', 'User', 'Temple', 'Amulet', 'Checkin']