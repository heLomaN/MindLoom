# src/engine/executor/action/action.py

from config import root_path
from engine.executor.executor import Executor
from services.rabbitmq.rabbitmq_producer import NoneBlockingMQClient, load_mq_config_parameters
import threading
import uuid
import json
import time

class Action(Executor):
    def __init__(self, id, secret):
        super().__init__(id, secret)
        parameters = load_mq_config_parameters()
        self.mq_client = NoneBlockingMQClient(parameters)
        self.lock = threading.Lock()  # 使用线程锁来确保线程安全

    def run(self, inputs):
        correlation_id = str(uuid.uuid4())
        request_message = json.dumps({
            "action_id": self.template.get("action_id"),
            "request_id": inputs.get("request_id"),
            "action_name": inputs.get("action_name"),
            "overtime": inputs.get("overtime"),
            "inputs": inputs.get("inputs"),
            "correlation_id": correlation_id
        })
        
        self.mq_client.send_one_msg('request_queue', request_message)

        timeout = int(inputs.get("overtime", 30))  # 将 overtime 转换为整数
        start_time = time.time()

        while True:
            response = self.mq_client.fetch_one_msg('response_queue')
            
            # 处理队列为空的情况
            if response is None:
                break
            
            response_data = json.loads(response)
            if response_data.get('correlation_id') == correlation_id:
                return json.loads(response_data['output'])  # 返回解码后的输出数据
            else:
                self.mq_client.send_one_msg('response_queue', response)

            if time.time() - start_time > timeout:
                return {"error": "Message processing timed out."}

            time.sleep(1)

        return {"error": "No response received."}  # 当队列为空时返回错误

    def close(self):
        self.mq_client.close()