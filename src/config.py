# src/config.py

import os
import json

# 获取当前项目根目录
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# 配置文件路径
config_path = os.path.join(root_path, 'config/config.json')
default_config_path = os.path.join(root_path, 'config/default_config.json')

class Config:
    def __init__(self, config_path=config_path):
        # 如果 config.json 不存在，则使用 default_config.json
        self.config_path = config_path if os.path.exists(config_path) else default_config_path
        self.config = self.load_config()

    def load_config(self):
        try:
            with open(self.config_path, 'r') as config_file:
                config_data = json.load(config_file)

                # 检查并加载 MongoDB 和 RabbitMQ 配置
                if 'mongodb_config' not in config_data['prompts']:
                    raise KeyError("'mongodb_config' 配置项在配置文件中缺失。")
                
                if 'rabbitmq' not in config_data['actions']:
                    raise KeyError("'rabbitmq' 配置项在配置文件中缺失。")

                return config_data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"加载配置时出错: {e}")
            return {}
        except KeyError as ke:
            print(f"配置文件中缺失必需的配置项: {ke}")
            return {}

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
            print(f"保存配置文件时出错: {e}")

# 初始化配置
config = Config()

# LOG 配置
LOG_PATH = config.get('log_config.path', 'log/')
LOG_MODE = config.get('log_config.mode', 'debug')

# 模板加载方法
TEMPLATE_LOAD_METHOD = config.get('prompts.default_source', 'file')
TEMPLATE_FILE_PATH = os.path.join(root_path, config.get('prompts.file_config.file_path', 'prompts'))

# MongoDB 配置
MONGO_CONFIG = config.get('prompts.mongodb_config')

# RabbitMQ 配置
RABBITMQ_CONFIG = config.get('actions.rabbitmq')
