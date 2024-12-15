# tests/tools_test.py

import unittest
import sys
import os

# 添加源代码目录到 Python 解释器路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from engine.executor.tool.tool_manager import ToolManager

class TestTask(unittest.TestCase):
    def test_run_case1(self):
        tm = ToolManager()
        tool_class = tm.load_tool('calculator.add')
        instant = tool_class()
        inputs = {'addend':1,'augend':2}
        print(instant.run(inputs))

if __name__ == '__main__':
    unittest.main()