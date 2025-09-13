import json, threading, pika
from app.settings import settings  

EXCHANGE = "events"
QUEUE = "user_service.q"           
ROUTING_KEYS = ["product.created"] 

def _callback(ch, method, properties, body):
    try:
        data = json.loads(body.decode("utf-8"))
        print(f"[events][user-service] {method.routing_key} -> {data}")
    except Exception as e:
        print(f"[events][user-service] error processing message: {e}")

def _start_consumer():
    params = pika.URLParameters(settings.RABBITMQ_URL)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    ch.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)

    ch.queue_declare(queue=QUEUE, durable=True)
    for key in ROUTING_KEYS:
        ch.queue_bind(exchange=EXCHANGE, queue=QUEUE, routing_key=key)

    ch.basic_consume(queue=QUEUE, on_message_callback=_callback, auto_ack=True)
    print(f"[events][user-service] consumer started on queue={QUEUE}, keys={ROUTING_KEYS}")
    ch.start_consuming()

def start_consumer_in_thread():
    t = threading.Thread(target=_start_consumer, daemon=True)
    t.start()
