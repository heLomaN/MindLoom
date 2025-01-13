# tests/test_rabbitmq_producer.py

import unittest
import sys
import os
import json
from bson import ObjectId

# 添加源代码目录到 Python 解释器路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from services.rabbitmq.rabbitmq_producer import load_mq_config_parameters, NoneBlockingMQClient

class TestRabbitMQProducer(unittest.TestCase):
    def setUp(self):
        self.parameters = load_mq_config_parameters()
        self.client = NoneBlockingMQClient(self.parameters)
        
        # 清空队列
        self.clear_queue('request_queue')
        self.clear_queue('response_queue')

    def clear_queue(self, queue_name):
        while True:
            message = self.client.fetch_one_msg(queue_name)
            if message is None:
                break

    def test_send_receive_message(self):
        message = {"test": "message"}
        self.client.send_one_msg('request_queue', json.dumps(message))

        # 模拟接收相同的消息
        received_message = self.client.fetch_one_msg('request_queue')
        self.assertEqual(json.loads(received_message), message)

    def tearDown(self):
        self.client.close()

if __name__ == '__main__':
    unittest.main()