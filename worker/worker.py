import time
import socket
import pika
from sklearn.datasets import fetch_california_housing

connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq-service"))
channel = connection.channel()

channel.queue_declare(queue="task_queue", durable=True)
print(" [*] Waiting for messages. To exit press CTRL+C")


def callback(ch, method, properties, body):
    print(f"[x] Received {body} on hostname {socket.gethostname()}")
    time.sleep(1)
    print("[x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


# j_data = json.loads(split[0])

# X,y = fetch_california_housing(return_X_y=True)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="task_queue", on_message_callback=callback)

channel.start_consuming()
