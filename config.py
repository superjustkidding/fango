# -*- coding: utf-8 -*-

import yaml
import os
from dotenv import load_dotenv

def load_config():
    load_dotenv()
    env_variables = os.getenv("DEVELOPMENT")
    env = os.environ.get('FLASK_ENV', env_variables)
    if env_variables == "development":
        config_file = "dev-config"
    elif env_variables == "production":
        config_file = "pro-config"
    else:
        config_file = "test-config"
    with open(f'config/{config_file}.yml', 'r') as f:
        config = yaml.safe_load(f)
    return config.get(env, {})
