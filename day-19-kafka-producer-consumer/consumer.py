"""
Reads all available messages from the 'orders' topic, from the very
beginning, and stops once nothing new arrives for 10 seconds - a
one-shot batch read rather than a never-ending stream, so this script
actually finishes for the purposes of this exercise.
"""
import json
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    "orders",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    consumer_timeout_ms=10000,
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
)

received = []
for message in consumer:
    event = message.value
    received.append(event)
    print(f"Received order_id={event['order_id']} (partition={message.partition}, offset={message.offset}): {event}")

consumer.close()
print(f"\nDone. Received {len(received)} messages.")

order_ids = sorted(e["order_id"] for e in received)
expected = list(range(1, 21))
print(f"Order IDs received: {order_ids}")
print(f"Matches expected 1-20 exactly: {order_ids == expected}")
