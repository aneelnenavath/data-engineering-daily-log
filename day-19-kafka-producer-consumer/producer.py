"""
Produces a batch of synthetic order events to the 'orders' Kafka topic,
then confirms exactly how many messages were sent.
"""
import json
import time
import random
from kafka import KafkaProducer

random.seed(42)

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

NUM_MESSAGES = 20
sent = 0

for order_id in range(1, NUM_MESSAGES + 1):
    event = {
        "order_id": order_id,
        "customer_id": random.randint(1, 10),
        "amount": round(random.uniform(10, 500), 2),
        "timestamp": time.time(),
    }
    producer.send("orders", value=event)
    sent += 1
    print(f"Sent order_id={order_id}: {event}")

producer.flush()
producer.close()
print(f"\nDone. Sent {sent} messages to topic 'orders'.")
