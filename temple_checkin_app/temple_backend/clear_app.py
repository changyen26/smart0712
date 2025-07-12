#!/usr/bin/env python3
"""
平安符打卡系統 - MySQL 版本 (使用 XAMPP)
"""
import os
import uuid
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

# 建立 Flask 應用程式
app = Flask(__name__)

# MySQL 設定 (XAMPP 預設設定)
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_USER = 'root'  # XAMPP 預設使用者
MYSQL_PASSWORD = ''  # XAMPP 預設無密碼，如果您設定了密碼請填入
MYSQL_DATABASE = 'temple_checkin'

# 應用程式設定
app.config['SECRET_KEY'] = 'temple-checkin-secret-key-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,  # 自動檢測連線是否有效
    'pool_recycle': 300,    # 5分鐘後重新建立連線
    'pool_timeout': 20,     # 連線池超時時間
    'max_overflow': 20,     # 連線池最大溢出數量
}
app.config['JWT_SECRET_KEY'] = 'temple-jwt-secret-2025'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# 初始化擴展
db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()

# 初始化應用程式
db.init_app(app)
jwt.init_app(app)
cors.init_app(app)

# =============================================================================
# 資料庫模型
# =============================================================================

class User(db.Model):
    """使用者模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)  # MySQL 建議使用 255
    blessing_points = db.Column(db.Integer, default=0, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'blessing_points': self.blessing_points,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Amulet(db.Model):
    """平安符模型"""
    __tablename__ = 'amulets'
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    uid = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'uid': self.uid,
            'name': self.name,
            'description': self.description,
            'image_url': self.image_url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Temple(db.Model):
    """廟宇模型"""
    __tablename__ = 'temples'
    
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    main_deity = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.DECIMAL(10, 8), nullable=False, index=True)  # 使用 DECIMAL 提高精度
    longitude = db.Column(db.DECIMAL(11, 8), nullable=False, index=True)
    blessing_bonus = db.Column(db.Integer, default=1, nullable=False)
    phone = db.Column(db.String(20))
    website = db.Column(db.Text)
    opening_hours = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'main_deity': self.main_deity,
            'description': self.description,
            'address': self.address,
            'latitude': float(self.latitude),  # 轉換 DECIMAL 為 float
            'longitude': float(self.longitude),
            'blessing_bonus': self.blessing_bonus,
            'phone': self.phone,
            'website': self.website,
            'opening_hours': self.opening_hours,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Checkin(db.Model):
    """打卡記錄模型"""
    __tablename__ = 'checkins'
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    temple_id = db.Column(db.String(36), db.ForeignKey('temples.id'), nullable=False, index=True)
    amulet_id = db.Column(db.String(36), db.ForeignKey('amulets.id'), nullable=False, index=True)
    points_earned = db.Column(db.Integer, nullable=False)
    checkin_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    notes = db.Column(db.Text)
    extra_data = db.Column(db.JSON)  # MySQL 5.7+ 支援 JSON 類型
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'temple_id': self.temple_id,
            'amulet_id': self.amulet_id,
            'points_earned': self.points_earned,
            'checkin_time': self.checkin_time.isoformat(),
            'notes': self.notes,
            'extra_data': self.extra_data
        }

# =============================================================================
# 輔助函數
# =============================================================================

def success_response(data=None, message='成功'):
    return jsonify({
        'success': True,
        'message': message,
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    })

def error_response(message='發生錯誤', status_code=400):
    return jsonify({
        'success': False,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }), status_code

def generate_amulet_uid():
    return uuid.uuid4().hex[:8].upper()

def test_database_connection():
    """測試資料庫連線"""
    try:
        # 測試連線並檢查資料表是否存在
        with db.engine.connect() as connection:
            result = connection.execute(db.text("SHOW TABLES LIKE 'users'"))
            tables_exist = result.fetchone() is not None
            return tables_exist
    except Exception as e:
        print(f"資料庫連線失敗: {e}")
        return False

# =============================================================================
# API 路由
# =============================================================================

@app.route('/')
def index():
    db_status = "connected" if test_database_connection() else "disconnected"
    return success_response({
        'name': '平安符打卡系統 API (MySQL 版)',
        'version': '1.0.0',
        'status': 'running',
        'database': db_status,
        'database_type': 'MySQL (手動建立)',
        'note': '資料庫已手動建立，包含測試資料',
        'test_accounts': {
            'user': 'test@example.com / password123',
            'admin': 'admin@example.com / admin123'
        },
        'endpoints': {
            'auth': '/api/auth',
            'temples': '/api/temples',
            'checkin': '/api/checkin'
        }
    })

@app.route('/health')
def health():
    db_connected = test_database_connection()
    
    health_info = {
        'status': 'healthy' if db_connected else 'unhealthy',
        'database': 'connected' if db_connected else 'disconnected',
        'database_type': 'MySQL (XAMPP)',
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if db_connected:
        try:
            # 取得一些統計資訊
            user_count = User.query.count()
            temple_count = Temple.query.filter_by(is_active=True).count()
            checkin_count = Checkin.query.count()
            
            health_info['statistics'] = {
                'total_users': user_count,
                'active_temples': temple_count,
                'total_checkins': checkin_count
            }
        except:
            pass
    
    return success_response(health_info)

# =============================================================================
# 認證相關 API
# =============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data:
            return error_response('請提供 JSON 資料')
        
        # 驗證必要欄位
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return error_response(f'缺少必要欄位: {field}')
        
        username = data['username'].strip()
        email = data['email'].strip()
        password = data['password']
        
        # 檢查是否已存在
        if User.query.filter_by(email=email).first():
            return error_response('電子郵件已被註冊')
        
        if User.query.filter_by(username=username).first():
            return error_response('使用者名稱已存在')
        
        # 建立新使用者
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            username=username,
            email=email
        )
        user.set_password(password)
        
        # 建立預設平安符
        amulet_id = str(uuid.uuid4())
        amulet = Amulet(
            id=amulet_id,
            user_id=user_id,
            uid=generate_amulet_uid(),
            name=f"{username}的平安符",
            description='系統自動生成的平安符'
        )
        
        db.session.add(user)
        db.session.add(amulet)
        db.session.commit()
        
        # 生成 JWT token
        access_token = create_access_token(identity=user_id)
        
        return success_response({
            'user': user.to_dict(),
            'amulet': amulet.to_dict(),
            'access_token': access_token
        }, '註冊成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'註冊失敗: {str(e)}', 500)

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data:
            return error_response('請提供 JSON 資料')
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return error_response('電子郵件和密碼為必填欄位')
        
        # 尋找使用者
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return error_response('電子郵件或密碼錯誤', 401)
        
        if not user.is_active:
            return error_response('帳戶已被停用', 403)
        
        # 取得使用者的平安符
        amulets = Amulet.query.filter_by(user_id=user.id, is_active=True).all()
        
        # 生成 JWT token
        access_token = create_access_token(identity=user.id)
        
        return success_response({
            'user': user.to_dict(),
            'amulets': [amulet.to_dict() for amulet in amulets],
            'access_token': access_token
        }, '登入成功')
        
    except Exception as e:
        return error_response(f'登入失敗: {str(e)}', 500)

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return error_response('使用者不存在', 404)
        
        amulets = Amulet.query.filter_by(user_id=user.id, is_active=True).all()
        
        return success_response({
            'user': user.to_dict(),
            'amulets': [amulet.to_dict() for amulet in amulets]
        })
        
    except Exception as e:
        return error_response(f'取得使用者資訊失敗: {str(e)}', 500)

# =============================================================================
# 廟宇相關 API
# =============================================================================

@app.route('/api/temples', methods=['GET'])
def get_temples():
    try:
        temples = Temple.query.filter_by(is_active=True).all()
        return success_response([temple.to_dict() for temple in temples])
    except Exception as e:
        return error_response(f'取得廟宇列表失敗: {str(e)}', 500)

@app.route('/api/temples/<temple_id>', methods=['GET'])
def get_temple(temple_id):
    try:
        temple = Temple.query.get(temple_id)
        if not temple or not temple.is_active:
            return error_response('廟宇不存在', 404)
        
        return success_response(temple.to_dict())
    except Exception as e:
        return error_response(f'取得廟宇資訊失敗: {str(e)}', 500)

# =============================================================================
# 打卡相關 API
# =============================================================================

@app.route('/api/checkin', methods=['POST'])
@jwt_required()
def create_checkin():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return error_response('請提供 JSON 資料')
        
        temple_id = data.get('temple_id')
        amulet_uid = data.get('amulet_uid')
        
        if not temple_id or not amulet_uid:
            return error_response('缺少必要欄位: temple_id, amulet_uid')
        
        # 檢查廟宇是否存在
        temple = Temple.query.get(temple_id)
        if not temple or not temple.is_active:
            return error_response('廟宇不存在或已停用', 404)
        
        # 檢查平安符是否存在且屬於當前使用者
        amulet = Amulet.query.filter_by(uid=amulet_uid, user_id=user_id, is_active=True).first()
        if not amulet:
            return error_response('平安符不存在或不屬於您', 404)
        
        # 檢查是否在24小時內已打卡
        time_limit = datetime.utcnow() - timedelta(hours=24)
        recent_checkin = Checkin.query.filter(
            Checkin.user_id == user_id,
            Checkin.temple_id == temple_id,
            Checkin.checkin_time >= time_limit
        ).first()
        
        if recent_checkin:
            return error_response('您在24小時內已在此廟宇打卡過了', 400)
        
        # 計算獲得的福報值
        points_earned = temple.blessing_bonus
        
        # 建立打卡記錄
        checkin = Checkin(
            id=str(uuid.uuid4()),
            user_id=user_id,
            temple_id=temple_id,
            amulet_id=amulet.id,
            points_earned=points_earned,
            notes=data.get('notes', ''),
            extra_data=data.get('extra_data', {})
        )
        
        # 更新使用者福報值
        user = User.query.get(user_id)
        user.blessing_points += points_earned
        user.updated_at = datetime.utcnow()
        
        db.session.add(checkin)
        db.session.commit()
        
        return success_response({
            'checkin': checkin.to_dict(),
            'temple': temple.to_dict(),
            'points_earned': points_earned,
            'total_blessing_points': user.blessing_points
        }, '打卡成功！')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'打卡失敗: {str(e)}', 500)

@app.route('/api/checkin/history', methods=['GET'])
@jwt_required()
def get_checkin_history():
    try:
        user_id = get_jwt_identity()
        checkins = Checkin.query.filter_by(user_id=user_id).order_by(Checkin.checkin_time.desc()).limit(50).all()
        
        # 包含廟宇資訊
        result = []
        for checkin in checkins:
            checkin_data = checkin.to_dict()
            temple = Temple.query.get(checkin.temple_id)
            if temple:
                checkin_data['temple'] = temple.to_dict()
            result.append(checkin_data)
        
        return success_response(result)
    except Exception as e:
        return error_response(f'取得打卡歷史失敗: {str(e)}', 500)

# =============================================================================
# CLI 指令和初始化 (已移除自動建立資料庫功能)
# =============================================================================

@app.cli.command()
def check_db():
    """檢查資料庫連線和資料表狀態"""
    print('正在檢查資料庫連線...')
    
    try:
        with db.engine.connect() as connection:
            print('✅ 資料庫連線成功')
            
            # 檢查資料表
            tables = ['users', 'temples', 'amulets', 'checkins']
            for table in tables:
                result = connection.execute(db.text(f"SHOW TABLES LIKE '{table}'"))
                if result.fetchone():
                    # 取得資料表記錄數
                    count_result = connection.execute(db.text(f"SELECT COUNT(*) FROM {table}"))
                    count = count_result.fetchone()[0]
                    print(f'✅ 資料表 {table}: {count} 筆記錄')
                else:
                    print(f'❌ 資料表 {table}: 不存在')
                    
    except Exception as e:
        print(f'❌ 資料庫檢查失敗: {e}')

@app.cli.command()
def reset_passwords():
    """重置測試帳戶密碼"""
    print('正在重置測試帳戶密碼...')
    
    try:
        # 重置測試使用者密碼
        test_user = User.query.filter_by(email='test@example.com').first()
        if test_user:
            test_user.set_password('password123')
            print('✅ 測試使用者密碼已重置為: password123')
        
        # 重置管理員密碼
        admin_user = User.query.filter_by(email='admin@example.com').first()
        if admin_user:
            admin_user.set_password('admin123')
            print('✅ 管理員密碼已重置為: admin123')
        
        db.session.commit()
        print('✅ 密碼重置完成！')
        
    except Exception as e:
        db.session.rollback()
        print(f'❌ 密碼重置失敗: {e}')

@app.cli.command()
def show_stats():
    """顯示系統統計資訊"""
    try:
        print('\n📊 系統統計資訊')
        print('=' * 50)
        
        # 使用者統計
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        admin_users = User.query.filter_by(is_admin=True).count()
        
        print(f'👥 使用者統計:')
        print(f'   總使用者數: {total_users}')
        print(f'   啟用使用者: {active_users}')
        print(f'   管理員數量: {admin_users}')
        
        # 廟宇統計
        total_temples = Temple.query.count()
        active_temples = Temple.query.filter_by(is_active=True).count()
        
        print(f'\n🏛️ 廟宇統計:')
        print(f'   總廟宇數: {total_temples}')
        print(f'   啟用廟宇: {active_temples}')
        
        # 打卡統計
        total_checkins = Checkin.query.count()
        today_checkins = Checkin.query.filter(
            db.func.date(Checkin.checkin_time) == db.func.curdate()
        ).count()
        
        print(f'\n✅ 打卡統計:')
        print(f'   總打卡數: {total_checkins}')
        print(f'   今日打卡: {today_checkins}')
        
        # 平安符統計
        total_amulets = Amulet.query.count()
        active_amulets = Amulet.query.filter_by(is_active=True).count()
        
        print(f'\n🏮 平安符統計:')
        print(f'   總平安符數: {total_amulets}')
        print(f'   啟用平安符: {active_amulets}')
        
    except Exception as e:
        print(f'❌ 取得統計資訊失敗: {e}')

# =============================================================================
# 主程式
# =============================================================================

if __name__ == '__main__':
    print('🚀 平安符打卡系統 API (MySQL 版) 啟動中...')
    print('📍 伺服器位址: http://127.0.0.1:5000')
    print('🗄️ 資料庫: MySQL (XAMPP) - 手動建立')
    print('📖 API 文件: http://127.0.0.1:5000/')
    print('🧪 測試介面: api_test.html')
    
    # 檢查資料庫連線
    with app.app_context():
        if test_database_connection():
            print('✅ 資料庫連線成功')
            
            # 檢查測試帳戶
            try:
                test_user = User.query.filter_by(email='test@example.com').first()
                admin_user = User.query.filter_by(email='admin@example.com').first()
                
                if test_user and admin_user:
                    print('✅ 測試帳戶確認存在')
                    print('   👤 測試使用者: test@example.com / password123')
                    print('   🔧 管理員: admin@example.com / admin123')
                else:
                    print('⚠️  測試帳戶可能不存在，請檢查資料庫')
                    
            except Exception as e:
                print(f'⚠️  無法檢查測試帳戶: {e}')
        else:
            print('❌ 資料庫連線失敗')
            print('💡 請確保:')
            print('   1. XAMPP MySQL 正在運行')
            print('   2. 資料庫 temple_checkin 已建立')
            print('   3. 資料表已透過 SQL 建立')
            print('   4. 測試資料已插入')
    
    print('\n🔧 可用的 CLI 指令:')
    print('   python clean_app.py check-db     # 檢查資料庫狀態')
    print('   python clean_app.py reset-passwords  # 重置測試帳戶密碼')
    print('   python clean_app.py show-stats   # 顯示系統統計')
    print('\n' + '='*60)
    
    app.run(debug=True, host='127.0.0.1', port=5000)

# 初始化擴展
db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()

# 初始化應用程式
db.init_app(app)
jwt.init_app(app)
cors.init_app(app)

# =============================================================================
# 資料庫模型
# =============================================================================

class User(db.Model):
    """使用者模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    blessing_points = db.Column(db.Integer, default=0)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'blessing_points': self.blessing_points,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class Amulet(db.Model):
    """平安符模型"""
    __tablename__ = 'amulets'
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    uid = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'uid': self.uid,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class Temple(db.Model):
    """廟宇模型"""
    __tablename__ = 'temples'
    
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    main_deity = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    blessing_bonus = db.Column(db.Integer, default=1)
    phone = db.Column(db.String(20))
    opening_hours = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'main_deity': self.main_deity,
            'description': self.description,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'blessing_bonus': self.blessing_bonus,
            'phone': self.phone,
            'opening_hours': self.opening_hours,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class Checkin(db.Model):
    """打卡記錄模型"""
    __tablename__ = 'checkins'
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    temple_id = db.Column(db.String(36), db.ForeignKey('temples.id'), nullable=False)
    amulet_id = db.Column(db.String(36), db.ForeignKey('amulets.id'), nullable=False)
    points_earned = db.Column(db.Integer, nullable=False)
    checkin_time = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'temple_id': self.temple_id,
            'amulet_id': self.amulet_id,
            'points_earned': self.points_earned,
            'checkin_time': self.checkin_time.isoformat(),
            'notes': self.notes
        }

# =============================================================================
# 輔助函數
# =============================================================================

def success_response(data=None, message='成功'):
    return jsonify({
        'success': True,
        'message': message,
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    })

def error_response(message='發生錯誤', status_code=400):
    return jsonify({
        'success': False,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }), status_code

def generate_amulet_uid():
    return uuid.uuid4().hex[:8].upper()

# =============================================================================
# API 路由
# =============================================================================

@app.route('/')
def index():
    return success_response({
        'name': '平安符打卡系統 API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'auth': '/api/auth',
            'temples': '/api/temples',
            'checkin': '/api/checkin'
        }
    })

@app.route('/health')
def health():
    return success_response({'status': 'healthy'})

# =============================================================================
# 認證相關 API
# =============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data:
            return error_response('請提供 JSON 資料')
        
        # 驗證必要欄位
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return error_response(f'缺少必要欄位: {field}')
        
        username = data['username'].strip()
        email = data['email'].strip()
        password = data['password']
        
        # 檢查是否已存在
        if User.query.filter_by(email=email).first():
            return error_response('電子郵件已被註冊')
        
        if User.query.filter_by(username=username).first():
            return error_response('使用者名稱已存在')
        
        # 建立新使用者
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            username=username,
            email=email
        )
        user.set_password(password)
        
        # 建立預設平安符
        amulet_id = str(uuid.uuid4())
        amulet = Amulet(
            id=amulet_id,
            user_id=user_id,
            uid=generate_amulet_uid(),
            name=f"{username}的平安符",
            description='系統自動生成的平安符'
        )
        
        db.session.add(user)
        db.session.add(amulet)
        db.session.commit()
        
        # 生成 JWT token
        access_token = create_access_token(identity=user_id)
        
        return success_response({
            'user': user.to_dict(),
            'amulet': amulet.to_dict(),
            'access_token': access_token
        }, '註冊成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'註冊失敗: {str(e)}', 500)

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data:
            return error_response('請提供 JSON 資料')
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return error_response('電子郵件和密碼為必填欄位')
        
        # 尋找使用者
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return error_response('電子郵件或密碼錯誤', 401)
        
        if not user.is_active:
            return error_response('帳戶已被停用', 403)
        
        # 取得使用者的平安符
        amulets = Amulet.query.filter_by(user_id=user.id, is_active=True).all()
        
        # 生成 JWT token
        access_token = create_access_token(identity=user.id)
        
        return success_response({
            'user': user.to_dict(),
            'amulets': [amulet.to_dict() for amulet in amulets],
            'access_token': access_token
        }, '登入成功')
        
    except Exception as e:
        return error_response(f'登入失敗: {str(e)}', 500)

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return error_response('使用者不存在', 404)
        
        amulets = Amulet.query.filter_by(user_id=user.id, is_active=True).all()
        
        return success_response({
            'user': user.to_dict(),
            'amulets': [amulet.to_dict() for amulet in amulets]
        })
        
    except Exception as e:
        return error_response(f'取得使用者資訊失敗: {str(e)}', 500)

# =============================================================================
# 廟宇相關 API
# =============================================================================

@app.route('/api/temples', methods=['GET'])
def get_temples():
    try:
        temples = Temple.query.filter_by(is_active=True).all()
        return success_response([temple.to_dict() for temple in temples])
    except Exception as e:
        return error_response(f'取得廟宇列表失敗: {str(e)}', 500)

@app.route('/api/temples/<temple_id>', methods=['GET'])
def get_temple(temple_id):
    try:
        temple = Temple.query.get(temple_id)
        if not temple or not temple.is_active:
            return error_response('廟宇不存在', 404)
        
        return success_response(temple.to_dict())
    except Exception as e:
        return error_response(f'取得廟宇資訊失敗: {str(e)}', 500)

# =============================================================================
# 打卡相關 API
# =============================================================================

@app.route('/api/checkin', methods=['POST'])
@jwt_required()
def create_checkin():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return error_response('請提供 JSON 資料')
        
        temple_id = data.get('temple_id')
        amulet_uid = data.get('amulet_uid')
        
        if not temple_id or not amulet_uid:
            return error_response('缺少必要欄位: temple_id, amulet_uid')
        
        # 檢查廟宇是否存在
        temple = Temple.query.get(temple_id)
        if not temple or not temple.is_active:
            return error_response('廟宇不存在或已停用', 404)
        
        # 檢查平安符是否存在且屬於當前使用者
        amulet = Amulet.query.filter_by(uid=amulet_uid, user_id=user_id, is_active=True).first()
        if not amulet:
            return error_response('平安符不存在或不屬於您', 404)
        
        # 檢查是否在24小時內已打卡
        time_limit = datetime.utcnow() - timedelta(hours=24)
        recent_checkin = Checkin.query.filter(
            Checkin.user_id == user_id,
            Checkin.temple_id == temple_id,
            Checkin.checkin_time >= time_limit
        ).first()
        
        if recent_checkin:
            return error_response('您在24小時內已在此廟宇打卡過了', 400)
        
        # 計算獲得的福報值
        points_earned = temple.blessing_bonus
        
        # 建立打卡記錄
        checkin = Checkin(
            id=str(uuid.uuid4()),
            user_id=user_id,
            temple_id=temple_id,
            amulet_id=amulet.id,
            points_earned=points_earned,
            notes=data.get('notes', '')
        )
        
        # 更新使用者福報值
        user = User.query.get(user_id)
        user.blessing_points += points_earned
        
        db.session.add(checkin)
        db.session.commit()
        
        return success_response({
            'checkin': checkin.to_dict(),
            'points_earned': points_earned,
            'total_blessing_points': user.blessing_points
        }, '打卡成功！')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'打卡失敗: {str(e)}', 500)

@app.route('/api/checkin/history', methods=['GET'])
@jwt_required()
def get_checkin_history():
    try:
        user_id = get_jwt_identity()
        checkins = Checkin.query.filter_by(user_id=user_id).order_by(Checkin.checkin_time.desc()).limit(50).all()
        
        return success_response([checkin.to_dict() for checkin in checkins])
    except Exception as e:
        return error_response(f'取得打卡歷史失敗: {str(e)}', 500)

# =============================================================================
# CLI 指令
# =============================================================================

@app.cli.command()
def init_db():
    """初始化資料庫"""
    print('正在建立資料庫表格...')
    db.create_all()
    print('資料庫表格建立完成！')

@app.cli.command()
def seed_db():
    """填入測試資料"""
    print('正在填入測試資料...')
    
    try:
        # 建立測試使用者
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            username='testuser',
            email='test@example.com',
            blessing_points=150
        )
        user.set_password('password123')
        
        # 建立測試平安符
        amulet = Amulet(
            id=str(uuid.uuid4()),
            user_id=user_id,
            uid='TESTUID1',
            name='測試平安符',
            description='這是一個測試用的平安符'
        )
        
        # 建立測試廟宇
        temples_data = [
            {
                'name': '龍山寺',
                'main_deity': '觀世音菩薩',
                'description': '台北市知名古剎，香火鼎盛。',
                'address': '台北市萬華區廣州街211號',
                'latitude': 25.0367,
                'longitude': 121.4999,
                'blessing_bonus': 3,
                'phone': '02-2302-5162',
                'opening_hours': '06:00-22:00'
            },
            {
                'name': '大甲鎮瀾宮',
                'main_deity': '天上聖母媽祖',
                'description': '台灣媽祖信仰的重要據點。',
                'address': '台中市大甲區順天路158號',
                'latitude': 24.3478,
                'longitude': 120.6248,
                'blessing_bonus': 5,
                'phone': '04-2676-3522',
                'opening_hours': '05:00-23:00'
            }
        ]
        
        db.session.add(user)
        db.session.add(amulet)
        
        for temple_data in temples_data:
            temple = Temple(id=str(uuid.uuid4()), **temple_data)
            db.session.add(temple)
        
        db.session.commit()
        print('測試資料填入完成！')
        print('測試帳戶: test@example.com / password123')
        
    except Exception as e:
        db.session.rollback()
        print(f'填入測試資料失敗: {str(e)}')

# =============================================================================
# 主程式
# =============================================================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print('🚀 平安符打卡系統 API 啟動中...')
        print('📍 伺服器位址: http://127.0.0.1:5000')
        print('📖 API 文件: http://127.0.0.1:5000/')
    
    app.run(debug=True, host='127.0.0.1', port=5000)