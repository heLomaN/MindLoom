import time

import pika
import json
import configparser
from src.services.logger.base_logger import BaseLogger

logger = BaseLogger("rabbitmq")

# 从INI文件中读取配置信息
def _load_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    return config

def load_mq_config_parameters():
    # 从config.ini文件中加载配置信息
    config = _load_config("config.ini")

    # 提取RabbitMQ的配置信息
    rabbitmq_config = config["rabbitmq"]
    username = rabbitmq_config["username"]
    password = rabbitmq_config["password"]
    host = rabbitmq_config["host"]
    port = int(rabbitmq_config["port"])

    credentials = pika.PlainCredentials(username=username, password=password)
    parameters = pika.ConnectionParameters(
        host=host,
        port=port,
        credentials=credentials
    )

    return parameters


class MQClient:
    def __init__(self, parameters):
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='request_queue', durable=True)
        self.channel.queue_declare(queue='response_queue', durable=True)

    def close(self):
        if self.connection.is_open:
            self.connection.close()


class BlockingMQClient(MQClient):
    def __init__(self, parameters):
        super().__init__(parameters)
        self.process = None

    def set_process(self, process):
        self.process = process

    def process_request(self, ch, method, props, body):
        data_rev = body.decode('utf-8')
        logger.info(f"Recv: {data_rev}")
        resp = self.process(data_rev)
        self.send_response(resp, props.correlation_id)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def send_response(self, response, correlation_id):
        self.channel.basic_publish(exchange='',
                                   routing_key='response_queue',
                                   properties=pika.BasicProperties(correlation_id=correlation_id),
                                   body=response)
        logger.info(f"Sent: {response}")

    def listen_for_requests(self):
        try:
            self.channel.basic_consume(queue='request_queue',
                                       on_message_callback=self.process_request)
            logger.info('Waiting for requests...')
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info('Interrupt received, stopping...')
        finally:
            self.connection.close()


class NoneBlockingMQClient(BlockingMQClient):
    def __init__(self, parameters):
        super.__init__(parameters)

    def fetch_one_msg(self, queue_name):
        method_frame, header_frame, body = self.channel.basic_get(queue=queue_name)
        if method_frame:
            data_rev = body.decode('utf-8')
            logger.info(f"Queue has messages. {data_rev}")
            return data_rev
        else:
            logger.info("Queue is empty.")
            return None

    def send_one_msg(self, queue_name, message):
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # 设置消息持久化
            )
        )
        logger.info(f"send msg {message}")
        return True


# Main function to control execution
def blocking_test():
    parameters = load_mq_config_parameters()
    client = BlockingMQClient(parameters)

    def append(data):
        return f"The resp to '{data}' is 'resp' : 'ack' ".encode('utf-8')

    try:
        client.set_process(append)
        client.listen_for_requests()
    except Exception as e:
        logger.error(f"Error occurred: {e}")
    finally:
        client.close()
        logger.info("Connection closed")


def non_blocking_test():
    '''
    non blocking mode
    '''
    parameters = load_mq_config_parameters()
    client = NoneBlockingMQClient(parameters)
    try:
        while True:
            if client.fetch_one_msg('request_queue'):
                client.send_one_msg("response_queue", "done")
            time.sleep(1)
    except Exception as e:
        logger.error(f"Error occurred: {e}")
    finally:
        client.close()
        logger.info("Connection closed")


if __name__ == '__main__':
    # non_blocking_test()
    blocking_test()