from kafka import KafkaProducer
import json

N = 25
producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)
for i in range(1, N + 1):
    producer.send('day25-events', {"id": i})
producer.flush()
producer.close()
print(f"PRODUCED_COUNT={N}")
