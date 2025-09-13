import json, pika
from app.config import settings

EXCHANGE = "events"
ROUTING_KEY = "product.created"

def _open_channel():
    params = pika.URLParameters(settings.RABBITMQ_URL)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    ch.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
    return conn, ch

def publish_product_created(product):
    """
    product: SQLAlchemy model instance (ima .id, .name, .sku)
    """
    conn, ch = _open_channel()
    try:
        payload = {
            "id": str(product.id),
            "name": product.name,
            "sku": product.sku,
        }
        ch.basic_publish(
            exchange=EXCHANGE,
            routing_key=ROUTING_KEY,
            body=json.dumps(payload).encode("utf-8"),
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2,  
            ),
        )
        print(f"[events] published: {ROUTING_KEY} -> {payload}")
    finally:
        try:
            ch.close()
        finally:
            conn.close()
