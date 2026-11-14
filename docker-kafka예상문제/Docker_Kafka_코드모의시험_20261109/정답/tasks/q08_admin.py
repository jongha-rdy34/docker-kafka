"""Q08 reference solution."""
TOPICS = {"mk-orders": 3, "mk-input": 1, "mk-output": 1}

def prepare_topics(admin):
    from kafka.admin import NewTopic
    existing = set(admin.list_topics())
    missing = sorted(set(TOPICS) - existing)
    if missing:
        admin.create_topics([NewTopic(name=n, num_partitions=TOPICS[n],
                                      replication_factor=1) for n in missing])
    return missing
