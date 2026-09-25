from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

for i in range(1, 31):
    event = {"id": i, "event": f"event-{i}"}
    producer.send('day21-events', event)
    print(f"Sent: {event}")

producer.flush()
producer.close()
print("All 30 messages sent.")
