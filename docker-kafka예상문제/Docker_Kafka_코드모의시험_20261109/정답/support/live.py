"""제공 실행기. tasks 함수만 수정하세요."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tasks"))
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient
import q08_admin, q09_producer, q10_consumer, q11_pipeline

p = argparse.ArgumentParser()
p.add_argument("action", choices=["admin", "produce", "consume", "pipeline"])
p.add_argument("--topic", default="mk-orders")
p.add_argument("--group", default="mk-reader-1")
a = p.parse_args()
b = "localhost:9092"
if a.action == "admin":
    c = KafkaAdminClient(bootstrap_servers=b, client_id="mk-admin")
    try:
        print(json.dumps(q08_admin.prepare_topics(c), ensure_ascii=False))
    finally:
        c.close()
elif a.action == "produce":
    records = [json.loads(s) for s in Path("data/orders.jsonl").read_text(encoding="utf-8").splitlines()]
    c = q09_producer.make_producer(KafkaProducer, b)
    try:
        print("sent=" + str(q09_producer.send_records(c, records)))
    finally:
        c.close()
elif a.action == "consume":
    c = q10_consumer.make_consumer(KafkaConsumer, a.topic, b, a.group)
    try:
        for row in q10_consumer.collect(c):
            print(json.dumps(row, ensure_ascii=False))
    finally:
        c.close()
else:
    # 연결 설정은 제공됩니다. Q11은 변환과 전달만 구현합니다.
    c = KafkaConsumer("mk-input", bootstrap_servers=b, group_id=a.group,
                      auto_offset_reset="earliest", enable_auto_commit=True,
                      consumer_timeout_ms=10000)
    producer = KafkaProducer(bootstrap_servers=b, value_serializer=str.encode)
    try:
        print("forwarded=" + str(q11_pipeline.relay(c, producer)))
    finally:
        producer.close()
        c.close()
