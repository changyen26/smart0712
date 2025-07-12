from werkzeug.security import generate_password_hash

# 生成測試使用者密碼雜湊
test_hash = generate_password_hash('password123')
admin_hash = generate_password_hash('admin123')

print(f"測試使用者密碼雜湊: {test_hash}")
print(f"管理員密碼雜湊: {admin_hash}")