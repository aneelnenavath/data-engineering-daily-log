from kafka import KafkaConsumer
import json, sys, os

LOG_FILE = "processed_log.txt"
MAX_MESSAGES = int(sys.argv[1]) if len(sys.argv) > 1 else 1000000

consumer = KafkaConsumer(
    'day21-events',
    bootstrap_servers='localhost:9092',
    group_id='day21-group',
    enable_auto_commit=False,
    auto_offset_reset='earliest',
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    consumer_timeout_ms=15000,
)

print(f"Consumer started (will hard-crash after {MAX_MESSAGES} messages this run). Waiting for messages...")

processed_this_run = 0
for message in consumer:
    event = message.value
    print(f"Processing id={event['id']} (partition={message.partition}, offset={message.offset})")
    with open(LOG_FILE, "a") as f:
        f.write(f"{event['id']}\n")
    consumer.commit()
    processed_this_run += 1
    if processed_this_run >= MAX_MESSAGES:
        print(f"--- Simulated crash after {processed_this_run} messages (no clean shutdown) ---")
        os._exit(1)

print("No more messages (timed out) - consumer exiting cleanly.")
consumer.close()
