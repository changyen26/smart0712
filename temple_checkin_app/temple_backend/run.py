#!/usr/bin/env python3
import os
from flask.cli import FlaskGroup
from app import create_app, db
from app.models import User, Amulet, Temple, Checkin

# 建立應用程式實例
app = create_app()
cli = FlaskGroup(app)

@app.shell_context_processor
def make_shell_context():
    """Flask Shell 上下文"""
    return {
        'db': db,
        'User': User,
        'Amulet': Amulet,
        'Temple': Temple,
        'Checkin': Checkin
    }

@app.cli.command()
def init_db():
    """初始化資料庫"""
    print('正在建立資料庫表格...')
    db.create_all()
    print('資料庫表格建立完成！')

@app.cli.command()
def reset_db():
    """重置資料庫"""
    print('正在重置資料庫...')
    db.drop_all()
    db.create_all()
    print('資料庫重置完成！')

@app.cli.command()
def seed_db():
    """填入測試資料"""
    from app.utils.helpers import generate_uuid, generate_amulet_uid
    import uuid
    
    print('正在填入測試資料...')
    
    try:
        # 建立測試使用者
        test_user_id = generate_uuid()
        test_user = User(
            id=test_user_id,
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        test_user.blessing_points = 150
        db.session.add(test_user)
        
        # 建立管理員使用者
        admin_user_id = generate_uuid()
        admin_user = User(
            id=admin_user_id,
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        admin_user.is_admin = True
        admin_user.blessing_points = 1000
        db.session.add(admin_user)
        
        # 建立測試平安符
        test_amulet_id = generate_uuid()
        test_amulet = Amulet(
            id=test_amulet_id,
            user_id=test_user_id,
            uid=generate_amulet_uid(),
            name='測試平安符',
            description='這是一個測試用的平安符'
        )
        db.session.add(test_amulet)
        
        admin_amulet_id = generate_uuid()
        admin_amulet = Amulet(
            id=admin_amulet_id,
            user_id=admin_user_id,
            uid=generate_amulet_uid(),
            name='管理員平安符',
            description='管理員專用平安符'
        )
        db.session.add(admin_amulet)
        
        # 建立測試廟宇
        temples_data = [
            {
                'id': generate_uuid(),
                'name': '龍山寺',
                'main_deity': '觀世音菩薩',
                'description': '台北市知名古剎，香火鼎盛，是信眾祈求平安的聖地。',
                'address': '台北市萬華區廣州街211號',
                'latitude': 25.0367,
                'longitude': 121.4999,
                'blessing_bonus': 3,
                'phone': '02-2302-5162',
                'opening_hours': '06:00-22:00'
            },
            {
                'id': generate_uuid(),
                'name': '大甲鎮瀾宮',
                'main_deity': '天上聖母媽祖',
                'description': '台灣媽祖信仰的重要據點，每年媽祖繞境活動聞名遐邇。',
                'address': '台中市大甲區順天路158號',
                'latitude': 24.3478,
                'longitude': 120.6248,
                'blessing_bonus': 5,
                'phone': '04-2676-3522',
                'opening_hours': '05:00-23:00'
            },
            {
                'id': generate_uuid(),
                'name': '行天宮',
                'main_deity': '關聖帝君',
                'description': '台北市香火最旺的廟宇之一，以靈驗著稱。',
                'address': '台北市中山區民權東路二段109號',
                'latitude': 25.0624,
                'longitude': 121.5336,
                'blessing_bonus': 2,
                'phone': '02-2502-7924',
                'opening_hours': '04:00-22:00'
            },
            {
                'id': generate_uuid(),
                'name': '台中樂成宮',
                'main_deity': '天上聖母',
                'description': '台中市旱溪媽祖廟，歷史悠久，信眾眾多。',
                'address': '台中市東區旱溪街48號',
                'latitude': 24.1477,
                'longitude': 120.6947,
                'blessing_bonus': 2,
                'phone': '04-2211-1928',
                'opening_hours': '05:30-22:00'
            },
            {
                'id': generate_uuid(),
                'name': '南投紫南宮',
                'main_deity': '福德正神',
                'description': '以求財聞名的土地公廟，香客絡繹不絕。',
                'address': '南投縣竹山鎮社寮里大公街40號',
                'latitude': 23.7500,
                'longitude': 120.6833,
                'blessing_bonus': 4,
                'phone': '049-262-3722',
                'opening_hours': '07:00-21:00'
            }
        ]
        
        for temple_data in temples_data:
            temple = Temple(**temple_data)
            db.session.add(temple)
        
        db.session.commit()
        print('測試資料填入完成！')
        
        print('\n測試帳戶資訊：')
        print('一般使用者: test@example.com / password123')
        print('管理員: admin@example.com / admin123')
        
    except Exception as e:
        db.session.rollback()
        print(f'填入測試資料失敗: {str(e)}')

@app.route('/')
def index():
    """API 根路徑"""
    return {
        'message': '平安符打卡系統 API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'auth': '/api/auth',
            'users': '/api/users',
            'temples': '/api/temples',
            'checkin': '/api/checkin',
            'amulets': '/api/amulets',
            'admin': '/api/admin'
        }
    }

@app.route('/health')
def health_check():
    """健康檢查"""
    try:
        # 簡單的資料庫連線測試
        db.session.execute(db.text('SELECT 1'))
        db_status = 'connected'
    except Exception:
        db_status = 'disconnected'
    
    return {
        'status': 'healthy',
        'database': db_status
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1', 'on']
    
    print(f'🚀 平安符打卡系統 API 啟動中...')
    print(f'📍 伺服器位址: http://{host}:{port}')
    print(f'🔧 除錯模式: {"開啟" if debug else "關閉"}')
    print(f'📖 API 文件: http://{host}:{port}/')
    
    app.run(host=host, port=port, debug=debug)