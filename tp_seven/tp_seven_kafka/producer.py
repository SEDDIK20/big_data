from kafka import KafkaProducer
import json
import time
import random

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

while True:
    data = {
        "device_id": "sensor_1",
        "temperature": round(random.uniform(20.0, 80.0), 2),
        "status": "ok"
    }
    producer.send("iot-data", value=data)
    print(f"Sent: {data}")
    time.sleep(2)
