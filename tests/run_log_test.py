# tests/run_log_test.py

import unittest
import sys
import os

# 添加源代码目录到 Python 解释器路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from engine.base.runtime_log import RuntimeLog

class TestTask(unittest.TestCase):
    def test_run_case(self):
        run_log = RuntimeLog(class_name='class', template_id='kslf', inputs=None, task_id=None, parent_run_id=None)
        run_log.add_record("这是一条记录")
        run_log.add_record("这又是一条记录")
        run_log.add_record("这又是一条记录")
        run_log.mark_as_failed({"系统错误！！！！"})

if __name__ == '__main__':
    unittest.main()