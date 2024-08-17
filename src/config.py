# src/config.py

import sys
import os
import json

# 获取当前项目根目录
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# 获取默认配置文件路径
config_path = os.path.join(root_path,'config/config.json')
default_config_path = os.path.join(root_path,'config/default_config.json')  # 如果不存在则读取 default_config.json
# 从文件中加载 JSON 数据
class Config:
    def __init__(self, config_path=config_path):
        self.config_path = config_path if os.path.exists(config_path) else default_config_path
        self.config = self.load_config()

    def load_config(self):
        try:
            with open(self.config_path, 'r') as config_file:
                config_data = json.load(config_file)
                
                # 检查'rabbitmq'键是否存在
                if 'rabbitmq' in config_data:
                    # 从环境变量中加载敏感信息
                    config_data['rabbitmq']['username'] = os.getenv('RABBITMQ_USERNAME', config_data['rabbitmq'].get('username'))
                    config_data['rabbitmq']['password'] = os.getenv('RABBITMQ_PASSWORD', config_data['rabbitmq'].get('password'))
                else:
                    raise KeyError("'rabbitmq' 配置项在配置文件中缺失。")

                return config_data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"加载配置时出错: {e}")
            return {}
        except KeyError as ke:
            print(f"配置文件中缺失必需的配置项: {ke}")
            return {}
        
    # Consider adding a method to refresh configuration
    def refresh_config(self):
        self.config = self.load_config()
        
    def get(self, key, default=None):
        keys = key.split('.')
        value = self.config
        try:
            for k in keys:
                value = value[k]
        except KeyError:
            return default
        return value

    def set(self, key, value):
        keys = key.split('.')
        d = self.config
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value
        self.save_config()

    def save_config(self):
        try:
            with open(self.config_path, 'w') as config_file:
                json.dump(self.config, config_file, indent=4)
        except IOError as e:
            print(f"Error saving configuration file: {e}")

# Initialize the configuration
config = Config()

# 获取 LOG 相关配置
LOG_PATH = config.get('log_config.path', 'log/')
LOG_MODE = config.get('log_config.mode', 'debug')

# 添加 TEMPLATE_LOAD_METHOD 和 TEMPLATE_FILE_PATH
TEMPLATE_LOAD_METHOD = config.get('prompts.default_source', 'file')
TEMPLATE_FILE_PATH = os.path.join(root_path, config.get('prompts.file_config.file_path', 'prompts'))


# 获取MongoDB 相关配置
MONGO_CONFIG = config.get('prompts.mongodb_config', {
    'host': config.get('prompts.mongodb_config.host', 'localhost'),
    'port': config.get('prompts.mongodb_config.port', 27017),
    'username': os.getenv('MONGO_USERNAME', config.get('prompts.mongodb_config.username', None)),
    'password': os.getenv('MONGO_PASSWORD', config.get('prompts.mongodb_config.password', None)),
    'db_name': config.get('prompts.mongodb_config.db_name', 'test'),
    'auth_source': config.get('prompts.mongodb_config.auth_source', 'admin')

    })
# if 'mongodb_config' in config_json:
#     MONGO_CONFIG = config_json['mongodb_config']