# %% [markdown]
# # Q09-3 결과 확인: clean-orders 소비
# - `clean-orders` 를 처음부터 소비하여 변환된 메시지를 출력합니다. (그룹 ID `output-checker`)
# - 받은 메시지를 리스트에 모아 마지막에 개수와 함께 출력합니다.

# %%
from kafka import KafkaConsumer

# %%
# TODO 1: clean-orders 를 구독하는 KafkaConsumer를 생성하세요.
consumer = KafkaConsumer(
    ⟪A:"clean-orders"⟫,
    bootstrap_servers=⟪A:"localhost:9092"⟫,
    auto_offset_reset=⟪A:"earliest"⟫,
    enable_auto_commit=True,
    group_id=⟪A:"output-checker"⟫,
    consumer_timeout_ms=10000,
)

# %%
# TODO 2: 메시지를 소비하여 출력하고 results 에 모으세요.
results = []
for message in ⟪A:consumer⟫:
    value = message.value.⟪A:decode("utf-8")⟫
    print(f"Consumed from clean-orders: {value}")
    results.append(value)

consumer.close()
print("results:", results, "count:", len(results))
