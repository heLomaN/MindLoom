# tests/weather_plan_test.py

import traceback
import unittest
import sys
import os

# 添加源代码目录到 Python 解释器路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from engine.executor.tool.tool import Tool
from engine.executor.generator.generator import Generator
from engine.executor.action.action import Action
from engine.scheduler.process.process import Process
from engine.scheduler.task.task import Task

class TestTask(unittest.TestCase):
    def test_run_case1(self):
        g_id = 'generate_planning0001'
        inputs = {
            'question' : '我想去天安门后天，什么时间合适？',
            'GNSS_address': 'Beijin',
            'local_time_string': '2024-12-02 18:34:24 Monday UTC+08:00+0800'
        }
        secret = None
        try:
            gen_instance = Generator(g_id, secret)
            result = gen_instance.run(inputs)
            print(result)
        except Generator.TemplateError as e:
            print("模板验证失败，错误信息如下：")
            for error in e.errors:
                print(f"- {error}")
        except Generator.ParameterError as e:
            print("参数校验失败，错误信息如下：")
            for error in e.errors:
                print(f"- {error}")
        except Exception as e:
            print(e)

    def test_run_case2(self):
        g_id = 'generate_planning0002'
        inputs = {
            'question' : '我想去天安门后天，什么时间合适？',
            'thinking': '',
            'weather_result': ''
        }
        secret = None
        try:
            gen_instance = Generator(g_id, secret)
            result = gen_instance.run(inputs)
            print(result)
        except Generator.TemplateError as e:
            print("模板验证失败，错误信息如下：")
            for error in e.errors:
                print(f"- {error}")
        except Generator.ParameterError as e:
            print("参数校验失败，错误信息如下：")
            for error in e.errors:
                print(f"- {error}")
        except Exception as e:
            traceback.print_exc()

    def test_run_case3(self):
        a_id = 'action_weather0001'
        inputs = {
            'location' : '我想去天安门后天，什么时间合适？',
            'start': 0,
            'days': 2
        }
        secret = None
        try:
            act_instance = Action(a_id, secret)
            result = act_instance.run(inputs)
            print(result)
        except Action.TemplateError as e:
            print("模板验证失败，错误信息如下：")
            for error in e.errors:
                print(f"- {error}")
        except Action.ParameterError as e:
            print("参数校验失败，错误信息如下：")
            for error in e.errors:
                print(f"- {error}")
        except Exception as e:
            traceback.print_exc()

    def test_run_case4(self):
        tl_id = 'local.local_time'
        inputs = {
            'timezone' : 'Asia/Shanghai'
        }
        tl_id2 = 'local.local_address'
        secret = None
        try:
            tool_instance = Tool(tl_id, secret)
            result = tool_instance.run(inputs)
            print(result)
            tool_instance = Tool(tl_id2, secret)
            result = tool_instance.run(inputs)
            print(result)
        except Tool.TemplateError as e:
            print("模板验证失败，错误信息如下：")
            for error in e.errors:
                print(f"- {error}")
        except Tool.ParameterError as e:
            print("参数校验失败，错误信息如下：")
            for error in e.errors:
                print(f"- {error}")
        except Exception as e:
            traceback.print_exc()

    def test_run_case5(self):
        p_id = 'process_planning0001'
        inputs = {
            'question' : '你好'
        }
        secret = None
        try:
            tool_instance = Process(p_id, secret)
            result = tool_instance.run(inputs)
            print(result)
        except Process.TemplateError as e:
            print("模板验证失败，错误信息如下：")
            for error in e.errors:
                print(f"- {error}")
        except Process.ParameterError as e:
            print("参数校验失败，错误信息如下：")
            for error in e.errors:
                print(f"- {error}")
        except Exception as e:
            traceback.print_exc()            
    # def test_run_case2(self):
    #     t_id = 'task_planning0001'
    #     inputs = {
    #         'question' : '我想去天安门后天，什么时间合适？',
    #     }
    #     secret = None
    #     try:
    #         task_instance = Task(t_id, secret)
    #         result = task_instance.run(inputs)
    #         print(result)
    #     except Exception as e:
    #         print(e)


if __name__ == '__main__':
    unittest.main()