# %% [markdown]
# # Q08-2 키별 파티션 검증 컨슈머 (region-orders)
# - `region-orders` 를 처음부터 읽고, 키·값·파티션을 출력합니다.
# - 키별로 들어간 파티션 집합을 만들어, 키마다 파티션이 1개뿐인지(OK) 확인합니다.
# - 컨슈머 그룹 ID는 `region-checker` 를 사용합니다.
# - `consumer_timeout_ms=10000` 은 10초 동안 새 메시지가 없으면 for문을 끝내기 위한 시험용 설정입니다(수정 금지).

# %%
from kafka import KafkaConsumer

# %%
# TODO 1: KafkaConsumer를 생성하세요.
consumer = KafkaConsumer(
    ⟪A:"region-orders"⟫,                  # 구독할 토픽
    bootstrap_servers="localhost:9092",
    auto_offset_reset=⟪A:"earliest"⟫,     # 커밋된 오프셋이 없으면 처음부터 읽기
    enable_auto_commit=True,
    group_id=⟪A:"region-checker"⟫,        # 컨슈머 그룹 ID
    consumer_timeout_ms=10000,
)

# %%
# TODO 2: 메시지를 소비하며 키·값·파티션을 출력하고, 키별 파티션 집합을 기록하세요.
partitions_by_key = {}
for message in ⟪A:consumer⟫:
    key = message.key.⟪A:decode("utf-8")⟫     # bytes → str
    value = message.value.⟪A:decode("utf-8")⟫
    print(f"Received: {value}, Key: {key}, Partition: {message.⟪A:partition⟫}")
    partitions_by_key.setdefault(key, set()).add(message.partition)

consumer.close()

# %%
# (제공) 키마다 파티션이 하나뿐이면 OK
for key, parts in sorted(partitions_by_key.items()):
    print(key, "->", sorted(parts), "OK" if len(parts) == 1 else "NG")
print("total keys:", len(partitions_by_key))
