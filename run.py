import os

from dotenv import load_dotenv
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

# 这里增加了flask在初始化的时候，判断没有管理员的情况下新增管理员账户
def create_initial_admin():
    load_dotenv()
    if not User.query.filter_by(is_admin=True).first():
        admin = User(
            username=os.getenv('ADMIN_USERNAME'),
            email=os.getenv('ADMIN_EMAIL'),
            password=generate_password_hash(os.getenv('ADMIN_PASSWORD')),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()

app = create_app()
with app.app_context():
    db.create_all()  # 创建加载数据表
    create_initial_admin()  # 创建超级管理员

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
