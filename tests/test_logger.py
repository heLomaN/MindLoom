# tests/test_logger.py

import unittest
import os
import sys

# 添加源代码目录到 Python 解释器路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from services.logger.base_logger import BaseLogger

class TestLogger(unittest.TestCase):
    def setUp(self):
        self.log_file = 'log/test_logger.log'
        self.logger = BaseLogger(name='test_logger', log_file=self.log_file).get_logger()

    def test_log_debug_message(self):
        self.logger.debug('This is a DEBUG message')
        self.assertTrue(self.check_log_contains('This is a DEBUG message'))

    def test_log_info_message(self):
        self.logger.info('This is an INFO message')
        self.assertTrue(self.check_log_contains('This is an INFO message'))

    def test_log_error_message(self):
        self.logger.error('This is an ERROR message')
        self.assertTrue(self.check_log_contains('This is an ERROR message'))

    def check_log_contains(self, text):
        with open(self.log_file, 'r') as file:
            log_content = file.read()
        return text in log_content

    def tearDown(self):
        # 关闭所有处理器并移除
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)
        
        # 删除日志文件
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

if __name__ == '__main__':
    unittest.main()