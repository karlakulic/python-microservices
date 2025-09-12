import os, json, time
import pika
from app.settings import settings

EXCHANGE = "events"
ROUTING_USER_CREATED = "user.created"

def _open_channel():
    params = pika.URLParameters(settings.RABBITMQ_URL)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    ch.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
    return conn, ch

def publish_user_created(payload: dict, retries: int = 5, backoff_s: float = 1.0):
    for attempt in range(1, retries+1):
        try:
            conn, ch = _open_channel()
            try:
                ch.basic_publish(
                    exchange=EXCHANGE,
                    routing_key=ROUTING_USER_CREATED,
                    body=json.dumps(payload).encode("utf-8"),
                    properties=pika.BasicProperties(
                        content_type="application/json",
                        delivery_mode=2,  
                    ),
                )
            finally:
                try: ch.close()
                finally: conn.close()
            print("[events] published: user.created")
            return
        except Exception as e:
            if attempt == retries:
                print(f"[events] publish failed after {retries} attempts: {e}")
                raise
            time.sleep(1)
