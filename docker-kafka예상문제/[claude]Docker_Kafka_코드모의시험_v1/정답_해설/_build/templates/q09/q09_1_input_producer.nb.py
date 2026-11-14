# %% [markdown]
# # Q09-1 입력 토픽 준비 (raw-orders, clean-orders)
# - `raw-orders`, `clean-orders` 가 있으면 삭제(각각 2초 대기)한 뒤, 둘 다 **파티션 1개 / 복제 계수 1**로 새로 생성합니다.
# - `raw-orders` 에 테스트 주문 메시지 5개를 전송합니다. (공백만 있는 메시지도 그대로 전송)

# %%
import time
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic

# %%
# TODO 1: KafkaAdminClient를 생성하세요.
admin_client = KafkaAdminClient(
    bootstrap_servers="localhost:9092",
    client_id="pipeline-admin"
)

input_topic = "raw-orders"
output_topic = "clean-orders"

# %%
# TODO 2: 두 토픽이 있으면 삭제한 뒤 새로 생성하세요.
existing_topics = admin_client.⟪A:list_topics⟫()
for topic in [input_topic, output_topic]:
    if topic in existing_topics:
        admin_client.⟪A:delete_topics⟫([topic])
        print(f"기존 토픽 '{topic}' 삭제 완료")
        time.sleep(2)

admin_client.⟪A:create_topics⟫([
    NewTopic(name=⟪A:input_topic⟫, num_partitions=1, replication_factor=1),
    NewTopic(name=⟪A:output_topic⟫, num_partitions=1, replication_factor=1),
])
print(f"새 토픽 '{input_topic}', '{output_topic}' 생성 완료")
admin_client.close()
time.sleep(2)  # (제공) 새 토픽의 리더가 준비될 때까지 대기. 바로 보내면 메시지가 조용히 유실될 수 있음

# %%
# TODO 3: 값만 문자열 → bytes 로 직렬화하는 KafkaProducer를 생성하세요. (키는 사용하지 않음)
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    ⟪A:value_serializer⟫=str.encode
)

# %%
# TODO 4: raw-orders 로 테스트 메시지를 전송하세요.
test_messages = [" coffee ", "tea", "   ", "latte", "Sandwich "]
for message in test_messages:
    producer.send(⟪A:input_topic⟫, value=⟪A:message⟫)
    print(f"Sent: {message!r}")

producer.⟪A:flush⟫()
producer.close()
