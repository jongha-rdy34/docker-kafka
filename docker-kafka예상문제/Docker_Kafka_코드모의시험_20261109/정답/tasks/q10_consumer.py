"""Q10 reference solution."""
def make_consumer(factory, topic, bootstrap, group):
    return factory(topic, bootstrap_servers=bootstrap, group_id=group,
                   auto_offset_reset="earliest", enable_auto_commit=True,
                   consumer_timeout_ms=10000)

def collect(consumer):
    result = []
    for message in consumer:
        result.append({"key": None if message.key is None else message.key.decode("utf-8"),
                       "value": message.value.decode("utf-8"),
                       "partition": message.partition, "offset": message.offset})
    return result
