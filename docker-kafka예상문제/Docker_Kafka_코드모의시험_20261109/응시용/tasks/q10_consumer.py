"""Q10: 역직렬화는 collect 안에서 수행합니다."""
def make_consumer(factory, topic, bootstrap, group):
    raise NotImplementedError("Q10 consumer options")

def collect(consumer):
    # 순회가 끝날 때까지 읽고 [{"key": str|None, "value": str,
    # "partition": int, "offset": int}, ...]를 반환합니다.
    raise NotImplementedError("Q10 decode")
