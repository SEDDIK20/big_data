from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "iot-data",
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for msg in consumer:
    data = msg.value
    print(f"Received: {data}")
    if data["temperature"] > 70:
        print("⚠️ ALERTE: Température élevée détectée!")
