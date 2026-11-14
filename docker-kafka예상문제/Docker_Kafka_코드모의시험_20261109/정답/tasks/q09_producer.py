"""Q09 reference solution."""
def make_producer(factory, bootstrap):
    return factory(bootstrap_servers=bootstrap,
                   key_serializer=str.encode, value_serializer=str.encode)

def send_records(producer, records):
    count = 0
    for record in records:
        producer.send("mk-orders", key=record["store"], value=record["text"]).get(timeout=10)
        count += 1
    producer.flush()
    return count
