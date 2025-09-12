import json
import pika 
from app.settings import settings

def publish_event(event_name: str, data: dict):
    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
    channel = connection.channel()
    channel.exchange_declare(exchange="events", exchange_type="fanout", durable=True)

    payload = {"event": event_name, "data": data}
    channel.basic_publish(
        exchange="events",
        routing_key="",
        body=json.dumps(payload),
        properties=pika.BasicProperties(content_type="application/json"),
    )
    connection.close()
    print(f"[events] published: {event_name} -> {payload}")

