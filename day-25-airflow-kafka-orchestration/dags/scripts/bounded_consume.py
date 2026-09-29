from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'day25-events',
    bootstrap_servers='kafka:9092',
    group_id='day25-group',
    auto_offset_reset='earliest',
    consumer_timeout_ms=15000,
)

count = 0
for message in consumer:
    count += 1
consumer.close()
print(f"CONSUMED_COUNT={count}")
