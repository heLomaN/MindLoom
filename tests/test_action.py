import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json
import uuid

# 添加源代码目录到 Python 解释器路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from engine.executor.action.action import Action

class TestAction(unittest.TestCase):
    def setUp(self):
        # 模拟加载的模板
        self.template = {
            "action_id": "wechat_check_login_status",
            "name": "WeChat Check Login Status",
            "description": "检查微信登录状态",
            "inputs": [
                {"name": "request_id", "type": "string", "description": "唯一的请求ID"},
                {"name": "action_name", "type": "string", "description": "执行的动作名称"},
                {"name": "overtime", "type": "string", "description": "操作超时时间（毫秒）"},
                {"name": "inputs", "type": "string", "description": "动作输入内容"}
            ],
            "outputs": [
                {"name": "output", "type": "string", "description": "操作的输出结果，包含JSON字符串"}
            ]
        }

        with patch.object(Action, 'load_template', return_value=self.template):
            self.action = Action(id='action_0001', secret='test_secret')

        # Mock MQ client methods
        self.action.mq_client = MagicMock()

        # 动态生成一个与 run 方法中一致的 correlation_id
        self.correlation_id = str(uuid.uuid4())

        self.action.mq_client.fetch_one_msg.side_effect = [
            json.dumps({
                "correlation_id": "some-other-id",
                "output": json.dumps({"status": "pending"})
            }),
            json.dumps({
                "correlation_id": self.correlation_id,
                "output": json.dumps({"status": "yes", "username": "caozhaku"})
            }),
            None  # 模拟队列为空的情况
        ]

        # Patch Action 类的 run 方法以使用一致的 correlation_id
        self.original_run = self.action.run

        def patched_run(inputs):
            with patch('uuid.uuid4', return_value=self.correlation_id):
                return self.original_run(inputs)

        self.action.run = patched_run

    def test_action_execution(self):
        inputs = {
            "request_id": "9a3b0c98-5d6e-4f02-a2e9-b87c68c41443",
            "action_name": "wechat_get",
            "overtime": "1000",  # 以字符串形式传递
            "inputs": "none"
        }
        result = self.action.run(inputs)
        self.assertEqual(result, {"status": "yes", "username": "caozhaku"})

    def tearDown(self):
        self.action.close()

if __name__ == '__main__':
    unittest.main()
