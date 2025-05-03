from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers=['<external_ip>:19092'])
producer.send('test_topic', b'Hello, Kafka!')
producer.flush()
print("Message sent")
