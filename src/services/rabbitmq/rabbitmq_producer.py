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

    def process(self, data):
        return f"The resp to '{data}' is 'resp' : 'ack' ".encode('utf-8')

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

    def close(self):
        if self.connection.is_open:
            self.connection.close()

# Main function to control execution
def main():
    parameters = load_mq_config_parameters()
    client = MQClient(parameters)
    try:
        client.listen_for_requests()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        client.close()

if __name__ == '__main__':
    main()