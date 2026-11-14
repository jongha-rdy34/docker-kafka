"""Q09: factory는 KafkaProducer 또는 테스트 대역입니다."""
def make_producer(factory, bootstrap):
    raise NotImplementedError("Q09 producer options")

def send_records(producer, records):
    # records: {"store": str, "text": str} 목록
    # send가 돌려준 Future의 get(timeout=10)으로 실패를 확인하세요.
    # 빈 목록도 flush하고 전송한 레코드 수를 반환합니다.
    raise NotImplementedError("Q09 send")
