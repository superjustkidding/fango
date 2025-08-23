# -*- coding: utf-8 -*-

import yaml
import os
from dotenv import load_dotenv
from datetime import timedelta


def load_config():
    load_dotenv()
    env = os.environ.get('FLASK_ENV', 'development')

    # 根据环境选择配置文件
    if env == "development":
        config_file = "dev-config"
    elif env == "production":
        config_file = "pro-config"
    else:
        config_file = "test-config"

    # 加载YAML配置文件
    with open(f'config/{config_file}.yml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 获取对应环境的配置
    env_config = config.get(env, {})

    # 环境变量覆盖配置文件中的值
    # 管理员配置
    env_config['ADMIN_USERNAME'] = os.environ.get('ADMIN_USERNAME', env_config.get('ADMIN_USERNAME', 'admin'))
    env_config['ADMIN_EMAIL'] = os.environ.get('ADMIN_EMAIL', env_config.get('ADMIN_EMAIL', 'admin@example.com'))
    env_config['ADMIN_PASSWORD'] = os.environ.get('ADMIN_PASSWORD', env_config.get('ADMIN_PASSWORD', 'admin123'))
    env_config['ADMIN_PHONE'] = os.environ.get('ADMIN_PHONE', env_config.get('ADMIN_PHONE', '18000000000'))

    # 日志配置
    env_config['LOG_LEVEL'] = os.environ.get('LOG_LEVEL', env_config.get('LOG_LEVEL', 'INFO'))
    env_config['LOG_TO_CONSOLE'] = os.environ.get('LOG_TO_CONSOLE',
                                                  str(env_config.get('LOG_TO_CONSOLE', True))).lower() == 'true'
    env_config['LOG_TO_MONGODB'] = os.environ.get('LOG_TO_MONGODB',
                                                  str(env_config.get('LOG_TO_MONGODB', False))).lower() == 'true'

    # MongoDB配置
    env_config['MONGODB_URI'] = os.environ.get('MONGODB_URI',
                                               env_config.get('MONGODB_URI', 'mongodb://localhost:27017/'))
    env_config['MONGODB_DB_NAME'] = os.environ.get('MONGODB_DB_NAME', env_config.get('MONGODB_DB_NAME', 'app_logs'))
    env_config['MONGODB_LOG_COLLECTION'] = os.environ.get('MONGODB_LOG_COLLECTION',
                                                          env_config.get('MONGODB_LOG_COLLECTION', 'flask_logs'))

    # CORS配置
    cors_origins = os.environ.get('CORS_ORIGINS', ','.join(
        env_config.get('CORS_ORIGINS', ['http://localhost:3000', 'http://127.0.0.1:3000'])))
    env_config['CORS_ORIGINS'] = cors_origins.split(',')

    # 转换JWT过期时间为timedelta对象
    if 'JWT_ACCESS_TOKEN_EXPIRES' in env_config and isinstance(env_config['JWT_ACCESS_TOKEN_EXPIRES'], int):
        env_config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=env_config['JWT_ACCESS_TOKEN_EXPIRES'])

    if 'JWT_REFRESH_TOKEN_EXPIRES' in env_config and isinstance(env_config['JWT_REFRESH_TOKEN_EXPIRES'], int):
        env_config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(seconds=env_config['JWT_REFRESH_TOKEN_EXPIRES'])

    return env_config