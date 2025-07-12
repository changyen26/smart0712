import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.config import config
from app.utils.helpers import CustomJSONEncoder

# 初始化擴展
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()

def create_app(config_name=None):
    """應用程式工廠函數"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 設定自定義 JSON 編碼器 (Flask 2.2+ 使用新方法)
    app.json.encoder = CustomJSONEncoder
    
    # 初始化擴展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, origins=app.config['CORS_ORIGINS'])
    
    # 註冊藍圖
    register_blueprints(app)
    
    # 註冊錯誤處理器
    register_error_handlers(app)
    
    # JWT 錯誤處理
    register_jwt_handlers(app)
    
    # 建立上傳目錄
    create_upload_directory(app)
    
    return app

def register_blueprints(app):
    """註冊藍圖"""
    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.temples import temples_bp
    from app.routes.checkin import checkin_bp
    from app.routes.amulets import amulets_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(temples_bp)
    app.register_blueprint(checkin_bp)
    app.register_blueprint(amulets_bp)
    app.register_blueprint(admin_bp)

def register_error_handlers(app):
    """註冊錯誤處理器"""
    from app.utils.helpers import error_response
    
    @app.errorhandler(400)
    def bad_request(error):
        return error_response('請求格式錯誤', status_code=400)
    
    @app.errorhandler(401)
    def unauthorized(error):
        return error_response('未授權存取', status_code=401)
    
    @app.errorhandler(403)
    def forbidden(error):
        return error_response('禁止存取', status_code=403)
    
    @app.errorhandler(404)
    def not_found(error):
        return error_response('資源不存在', status_code=404)
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return error_response('方法不允許', status_code=405)
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return error_response('伺服器內部錯誤', status_code=500)

def register_jwt_handlers(app):
    """註冊 JWT 錯誤處理器"""
    from app.utils.helpers import error_response
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return error_response('Token 已過期', status_code=401)
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return error_response('Token 無效', status_code=401)
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return error_response('需要提供 Token', status_code=401)
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return error_response('需要新的 Token', status_code=401)
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return error_response('Token 已被撤銷', status_code=401)

def create_upload_directory(app):
    """建立上傳目錄"""
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        
    # 建立子目錄
    subdirs = ['avatars', 'temples', 'amulets']
    for subdir in subdirs:
        path = os.path.join(upload_folder, subdir)
        if not os.path.exists(path):
            os.makedirs(path)