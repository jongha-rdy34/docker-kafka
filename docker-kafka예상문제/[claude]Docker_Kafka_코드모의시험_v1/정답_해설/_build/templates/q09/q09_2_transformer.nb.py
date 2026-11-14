# %% [markdown]
# # Q09-2 변환기: raw-orders → clean-orders
# - `raw-orders` 를 처음부터 소비합니다. (그룹 ID `transformer-group`)
# - 각 메시지를 문자열로 바꾼 뒤 **양 끝 공백 제거 → 대문자 변환** 하여 `clean-orders` 로 보냅니다.
# - 공백 제거 후 빈 문자열인 메시지는 보내지 않고 `Skipped empty message` 를 출력합니다.
# - 마지막에 flush 하고, 실제로 보낸 개수를 `forwarded=N` 형식으로 출력합니다.
# - `consumer_timeout_ms=10000` 은 시험용 설정입니다(수정 금지).

# %%
from kafka import KafkaConsumer, KafkaProducer

# %%
# TODO 1: raw-orders 를 구독하는 KafkaConsumer를 생성하세요.
consumer = KafkaConsumer(
    ⟪A:"raw-orders"⟫,
    bootstrap_servers="localhost:9092",
    auto_offset_reset=⟪A:"earliest"⟫,
    enable_auto_commit=⟪A:True⟫,
    group_id=⟪A:"transformer-group"⟫,
    consumer_timeout_ms=10000,
)

# %%
# TODO 2: 문자열 값을 bytes 로 직렬화하는 KafkaProducer를 생성하세요.
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=⟪A:str.encode⟫
)

# %%
# TODO 3: 변환 후 clean-orders 로 전송하세요.
sent = 0
for message in consumer:
    text = message.value.⟪A:decode("utf-8")⟫.⟪A:strip⟫()   # bytes → str, 양 끝 공백 제거
    if ⟪A:not text⟫:                                          # 빈 문자열이면 건너뛰기
        print("Skipped empty message")
        ⟪A:continue⟫
    transformed = text.⟪A:upper⟫()
    # [오류 수정] 아래 줄은 실행 시 TypeError가 발생합니다.
    ⟪B:producer.send("clean-orders", value=transformed.encode("utf-8"))‖producer.send("clean-orders", value=transformed)⟫
    sent += 1
    print(f"Transformed and Sent: {transformed}")

producer.⟪A:flush⟫()
print(f"forwarded={sent}")
consumer.close()
producer.close()
