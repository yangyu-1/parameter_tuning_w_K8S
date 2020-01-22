import time
import socket
import pika
from trainer import trainer
import json


connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq-service"))
channel = connection.channel()

channel.queue_declare(queue="task_queue", durable=True)
print(" [*] Waiting for messages. To exit press CTRL+C")


def callback(ch, method, properties, body):
    j_data = json.loads(body)
    print(f"{j_data}")
    print(f"{socket.gethostname()} ")
    trainer(j_data)
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="task_queue", on_message_callback=callback)

channel.start_consuming()
