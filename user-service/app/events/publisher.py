import os
import json
import pika
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

def _open_channel():
    params = pika.URLParameters(RABBITMQ_URL)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    ch.exchange_declare(exchange="users", exchange_type="topic", durable=True)
    return conn, ch

def publish_user_created(payload: dict):
    conn, ch = _open_channel()
    try:
        ch.basic_publish(
            exchange="users",
            routing_key="user.created",
            body=json.dumps(payload).encode("utf-8"),
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2,  
            ),
        )
    finally:
        try:
            ch.close()
        finally:
            conn.close()
