"""Optional real Kafka check; run after a single fresh Q09/Q11 execution."""
import argparse
import json
import time
from pathlib import Path
from collections import Counter, defaultdict
from kafka import KafkaConsumer, TopicPartition

p=argparse.ArgumentParser()
p.add_argument('mode',choices=['orders','pipeline'])
a=p.parse_args()
topic='mk-orders' if a.mode=='orders' else 'mk-output'
c=KafkaConsumer(bootstrap_servers='localhost:9092',group_id=None,
                enable_auto_commit=False,request_timeout_ms=30000)
try:
    partitions=c.partitions_for_topic(topic)
    expected_partitions=3 if a.mode=='orders' else 1
    assert partitions==set(range(expected_partitions)),('partition mismatch',partitions)
    tps=[TopicPartition(topic,i) for i in sorted(partitions)]
    c.assign(tps)
    ends=c.end_offsets(tps)
    c.seek_to_beginning(*tps)
    rows=[]
    deadline=time.monotonic()+20
    while any(c.position(tp)<ends[tp] for tp in tps):
        if time.monotonic()>deadline:raise TimeoutError('Could not read snapshot')
        for tp,messages in c.poll(timeout_ms=1000).items():
            rows.extend(m for m in messages if m.offset<ends[tp])
    if a.mode=='orders':
        expected=[json.loads(x) for x in Path('data/orders.jsonl').read_text(encoding='utf-8').splitlines()]
        actual=Counter((m.key.decode('utf-8'),m.value.decode('utf-8')) for m in rows)
        assert actual==Counter((r['store'],r['text']) for r in expected),('records mismatch',actual)
        seen=defaultdict(set)
        for m in rows:seen[m.key].add(m.partition)
        assert all(len(ps)==1 for ps in seen.values()),'same key crossed partitions'
    else:
        actual=[m.value.decode('utf-8') for m in sorted(rows,key=lambda m:m.offset)]
        assert actual==['COFFEE','TEA','한글'],('pipeline output mismatch',actual)
    print('PASS real Kafka snapshot: '+topic+' records='+str(len(rows)))
finally:
    c.close()
