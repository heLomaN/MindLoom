# tests/weather_plan_test.py

import unittest
import sys
import os

# 添加源代码目录到 Python 解释器路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from engine.scheduler.task.task import Task

class TestTask(unittest.TestCase):
    def test_run_case1(self):
        t_id = 'task_planning0001'
        inputs = {
            'question' : '我想去天安门后天，什么时间合适？',
        }
        secret = None
        try:
            task_instance = Task(t_id, secret)
            te = task_instance.get_template()
            print(te)
            # result = task_instance.run(inputs)
        except Exception as e:
            print(e)

        #print(result)
        # 这里编写断言来验证 run 方法的输出是否符合预期
        #self.assertEqual(result, {'answer': '哈哈哈哈'})

if __name__ == '__main__':
    unittest.main()