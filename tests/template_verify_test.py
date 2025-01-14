# tests/template_verify_test.py

import unittest
import sys
import os

# 添加源代码目录到 Python 解释器路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from engine.scheduler.task.task import Task

class TestTask(unittest.TestCase):
    def test_run_case1(self):
        template = {
            "name":'1',
            "description":'',
            "inputs": [],
            "outputs": None,
            "kkk": {},
            "execution": {
                "call": {
                    "class": "action",
                    "id": "unique_id_123",
                    "inputs": [
                        {"name": "input1", "type": "string"},
                        {"name": "input2", "type": "objec", "source": "kl"}
                    ],
                    "outputs": [
                        {"name": "sd", "type": "strig", "target": None }
                    ]
                }
            }
        }
        try:
            result = Task.validate_template(template)
            print("模板验证通过，结果如下：")
            print(result)
        except Task.TemplateError as e:
            print("模板验证失败，错误信息如下：")
            for error in e.errors:
                print(f"- {error}")

    def test_run_case2(self):
        t_id = 'task_template_test0001'
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

if __name__ == '__main__':
    unittest.main()