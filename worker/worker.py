import time
import pika
from trainer import trainer
import json
import socket

try:
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq-service", heartbeat=600)
    )
except socket.gaierror:
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost", heartbeat=600)
    )
channel = connection.channel()

channel.queue_declare(queue="task_queue", durable=True)
print(" [*] Waiting for messages. To exit press CTRL+C")


def callback(ch, method, properties, body):
    j_data = json.loads(body)
    trainer(j_data)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print("task complete. ready for new item")


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="task_queue", on_message_callback=callback)

channel.start_consuming()
