#!/usr/bin/env python3

import logging
import os
import sys
import time
from datetime import datetime

from auto_teacher_process.mq.rabbitmq_client import RabbitMQClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "172.22.121.63")
    rabbitmq_port = int(os.getenv("RABBITMQ_PORT", "30452"))
    rabbitmq_user = os.getenv("RABBITMQ_USER", "admin")
    rabbitmq_pass = os.getenv("RABBITMQ_PASS", "123456")
    queue_name = os.getenv("RABBITMQ_QUEUE", "test_queue")

    producer = RabbitMQClient(
        host=rabbitmq_host,
        port=rabbitmq_port,
        username=rabbitmq_user,
        password=rabbitmq_pass,
        queue_name=queue_name,
    )

    try:
        producer.connect()
        logger.info(f"Connected to RabbitMQ at {rabbitmq_host}:{rabbitmq_port}")

        message_count = 1
        while True:
            message = {
                "message_id": message_count,
                "content": f"Test message {message_count}",
                "timestamp": datetime.now().isoformat(),
            }

            producer.publish_message(message)
            logger.info(f"Sent message {message_count}")

            message_count += 1

            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("\nShutting down producer...")
        producer.close()

    except Exception as e:
        logger.info(f"Error: {e!s}")
        producer.close()
        sys.exit(1)


if __name__ == "__main__":
    main()
