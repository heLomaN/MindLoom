# src/services/logger/base_logger.py

import os
import logging
from logging.handlers import TimedRotatingFileHandler
from config import config  # 这里导入 config 对象

# 从配置文件中加载日志配置
LOG_PATH = config.get('log_config.path', 'log/')
LOG_MODE = config.get('log_config.mode', 'debug')
LOG_LEVEL = config.get('log_config.level', logging.DEBUG)

class BaseLogger:
    def __init__(self, name='mindloom', level=LOG_LEVEL, log_file=None):
        # Create log directory if it doesn't exist
        log_dir = LOG_PATH
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_file = log_file or os.path.join(log_dir, f'{name}.log')

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Log to console
        if LOG_MODE == 'debug':
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        # Log to file with automatic rotation
        backup_count = 0 if LOG_MODE == 'debug' else 180
        file_handler = TimedRotatingFileHandler(log_file, when='midnight', interval=1, backupCount=backup_count)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)

# 创建不同模块的日志记录器
def get_logger(module_name):
    log_file = os.path.join(LOG_PATH, f'{module_name}.log')
    logger = BaseLogger(name=module_name, level=LOG_LEVEL, log_file=log_file)
    return logger.get_logger()
