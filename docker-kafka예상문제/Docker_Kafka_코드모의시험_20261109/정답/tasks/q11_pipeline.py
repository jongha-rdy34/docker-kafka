"""Q11 reference solution."""
def transform(raw):
    value = raw.decode("utf-8").strip().upper()
    return value if value else None

def relay(consumer, producer):
    count = 0
    for message in consumer:
        value = transform(message.value)
        if value is not None:
            producer.send("mk-output", value=value).get(timeout=10)
            count += 1
    producer.flush()
    return count
