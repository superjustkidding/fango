import os
import logging
from flask_migrate import Migrate
from dotenv import load_dotenv
from app import create_app
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import OperationalError

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()


def create_initial_admin(app):
    """在应用上下文中创建初始管理员账户"""
    with app.app_context():
        try:
            # 延迟导入 - 确保所有模型已注册
            from app.models.users.user import User

            # 检查管理员是否存在
            if User.query.filter_by(is_admin=True).first():
                logger.info("管理员账户已存在，跳过创建")
                return

            # 获取环境变量
            username = os.getenv('ADMIN_USERNAME')
            email = os.getenv('ADMIN_EMAIL')
            password = os.getenv('ADMIN_PASSWORD')

            if not all([username, email, password]):
                raise ValueError("管理员环境变量未设置")

            # 创建管理员账户
            admin = User(
                username=username,
                email=email,
                password=generate_password_hash(password),
                is_admin=True
            )

            # 获取数据库实例
            from app import db
            db.session.add(admin)
            db.session.commit()
            logger.info(f"初始管理员账户创建成功: {username}")

        except OperationalError as e:
            logger.error(f"数据库操作失败: {str(e)}")
            logger.error("请确保数据库已初始化并运行迁移")
        except Exception as e:
            logger.error(f"创建管理员时发生未知错误: {str(e)}")


# 创建应用实例
app = create_app()
migrate = Migrate(app, app.db)  # 使用 app.db

# 创建初始管理员
create_initial_admin(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)