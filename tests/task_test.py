# tests/task_test.py

import traceback
import unittest
import sys
import os

# 添加源代码目录到 Python 解释器路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from engine.scheduler.task.task import Task

def extract_exception_messages(exc):
    """递归提取异常链中的错误信息"""
    messages = []
    while exc:
        exc_type = exc.__class__.__name__
        messages.append(f"{exc_type}: {exc}")
        exc = exc.__cause__  # 获取引发当前异常的原始异常
    return "\n".join(messages)  # 从底层异常到顶层异常

class TestTask(unittest.TestCase):
    def test_run_case(self):
        t_id = 'task_template_test0001'
        inputs = {
            'question' : '我想去天安门后天，什么时间合适？',
        }
        try:
            task_instance = Task(t_id)
            run_id,result = task_instance.run(inputs)
            print(result)
        except Task.TemplateError as e:
            print("模板验证失败，错误信息如下：")
            for error in e.errors:
                print(f"- {error}")
        except Task.ParameterError as e:
            print("参数校验失败，错误信息如下：")
            for error in e.errors:
                print(f"- {error}")
        except Exception as e:
            print(extract_exception_messages(e))

if __name__ == '__main__':
    unittest.main()