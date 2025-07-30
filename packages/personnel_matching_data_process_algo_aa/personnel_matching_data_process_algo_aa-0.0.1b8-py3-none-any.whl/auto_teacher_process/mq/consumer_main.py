#!/usr/bin/env python3

import json
import logging
import os
import sys

from auto_teacher_process.mq.rabbitmq_client import RabbitMQClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def process_message(ch, method, properties, body: bytes) -> None:
    """自定义的消息处理函数

    Args:
        ch: pika.Channel
        method: pika.spec.Basic.Deliver
        properties: pika.spec.BasicProperties
        body: bytes
    """
    try:
        message = json.loads(body.decode())
        logger.info(f"Received message: {message}")

        # TODO: 处理业务调用 run_worker

        # 处理成功，手动确认消息
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except json.JSONDecodeError:
        logger.warning(f"Received non-JSON message: {body.decode()}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        logger.error(f"Error processing message: {e!s}")
        # 处理失败，拒绝消息并重新入队
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def main():
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "172.22.121.63")
    rabbitmq_port = int(os.getenv("RABBITMQ_PORT", "30452"))
    rabbitmq_user = os.getenv("RABBITMQ_USER", "admin")
    rabbitmq_pass = os.getenv("RABBITMQ_PASS", "123456")
    queue_name = os.getenv("RABBITMQ_QUEUE", "test_queue")

    consumer = RabbitMQClient(
        host=rabbitmq_host,
        port=rabbitmq_port,
        username=rabbitmq_user,
        password=rabbitmq_pass,
        queue_name=queue_name,
    )

    try:
        consumer.connect()

        logger.info(f"Connected to RabbitMQ at {rabbitmq_host}:{rabbitmq_port}")
        logger.info(f"Consuming messages from queue: {queue_name}")
        logger.info("Press CTRL+C to exit")

        consumer.start_consuming(callback=process_message)

    except KeyboardInterrupt:
        logger.info("\nShutting down consumer...")
        consumer.close()

    except Exception as e:
        logger.error(f"Error: {e!s}")
        consumer.close()
        sys.exit(1)


if __name__ == "__main__":
    main()
