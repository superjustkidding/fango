import yaml
import os

def load_config():
    env = os.environ.get('FLASK_ENV', 'development')
    with open('config.yml', 'r') as f:
        config = yaml.safe_load(f)
    return config.get(env, {})