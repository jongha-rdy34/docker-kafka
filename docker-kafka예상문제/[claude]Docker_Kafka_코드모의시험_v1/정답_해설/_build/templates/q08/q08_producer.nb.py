# %% [markdown]
# # Q08-1 키 기반 프로듀서 (region-orders)
# - `region-orders` 토픽이 있으면 삭제 후 2초 대기, **파티션 3개 / 복제 계수 1**로 새로 생성합니다.
# - 지역명을 키로 하는 주문 메시지 9개를 전송하고, 같은 키가 같은 파티션으로 가는지 확인합니다.
# - 이 노트북은 **두 번 연속 실행해도** 오류 없이 동작해야 합니다.
# - `______` 를 채우고, `[오류 수정]` 표시가 있는 줄은 고치세요.

# %%
import time
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic

# %%
# TODO 1: KafkaAdminClient를 생성하세요.
admin_client = KafkaAdminClient(
    bootstrap_servers=⟪A:"localhost:9092"⟫,  # Kafka 브로커 주소
    client_id="region-admin"
)

topic_name = "region-orders"

# %%
# TODO 2: 토픽이 있으면 삭제하고 2초 대기한 뒤, 파티션 3개짜리 토픽을 새로 생성하세요.
existing_topics = admin_client.⟪A:list_topics⟫()  # 현재 토픽 목록 조회
if topic_name in existing_topics:
    # [오류 수정] 토픽이 이미 있을 때(두 번째 실행) 이 줄에서 오류가 발생합니다.
    ⟪B:admin_client.delete_topics(topic_name)‖admin_client.delete_topics([topic_name])⟫
    print(f"기존 토픽 '{topic_name}' 삭제 완료")
    time.sleep(2)

new_topic = NewTopic(name=topic_name, num_partitions=⟪A:3⟫, replication_factor=⟪A:1⟫)
admin_client.⟪A:create_topics⟫([new_topic])  # 토픽 생성
print(f"새 토픽 '{topic_name}' 생성 완료")

admin_client.⟪A:close⟫()  # AdminClient 연결 종료
time.sleep(2)  # (제공) 새 토픽의 리더가 준비될 때까지 대기

# %%
# TODO 3: 문자열 키와 값을 bytes로 직렬화하는 KafkaProducer를 생성하세요.
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    key_serializer=⟪A:str.encode⟫,    # 키 직렬화
    value_serializer=⟪A:str.encode⟫   # 값 직렬화
)

# %%
# TODO 4: regions를 순서대로 돌아가며 키로 사용해 order-0 ~ order-8 을 전송하세요.
regions = ["seoul", "daejeon", "ulsan"]
for i in range(9):
    key = regions[⟪A:i % len(regions)⟫]
    value = f"order-{i}"
    future = producer.⟪A:send⟫(topic_name, key=⟪A:key⟫, value=⟪A:value⟫)
    meta = future.get(timeout=10)  # (제공) 전송 결과의 파티션·오프셋 확인
    print(f"Sent: {value} key={key} -> partition {meta.partition}, offset {meta.offset}")

producer.⟪A:flush⟫()  # 버퍼에 남은 메시지를 모두 전송
producer.close()
