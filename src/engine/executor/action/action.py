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
        request_message = json.dumps(inputs)
        self.mq_client.send_one_msg('request_queue', request_message)

        start_time = time.time()
        timeout = 30  # 设置超时时间

        while True:
            with self.lock:
                response = self.mq_client.fetch_one_msg('response_queue')
                if response:
                    response_data = json.loads(response)
                    if response_data.get('correlation_id') == correlation_id:
                        return response_data['data']
                    else:
                        self.mq_client.send_one_msg('response_queue', response)
                if time.time() - start_time > timeout:
                    self.logger.error("Message processing timeout.")
                    return {}

            time.sleep(1)

    def close(self):
        """ 关闭MQ连接 """
        self.mq_client.close()