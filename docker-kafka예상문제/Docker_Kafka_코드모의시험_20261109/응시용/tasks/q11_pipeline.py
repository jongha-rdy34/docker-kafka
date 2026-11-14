"""Q11: 공백 제거 후 대문자 변환. 빈 값은 전송하지 않습니다."""
def transform(raw):
    # raw는 bytes. 유효하지 않은 UTF-8은 UnicodeDecodeError를 전파합니다.
    raise NotImplementedError("Q11 transform")

def relay(consumer, producer):
    # key는 사용하지 않습니다. 출력 토픽은 mk-output입니다.
    # Future.get(timeout=10)으로 전송 확인 후 마지막에 flush합니다.
    # 반환: 실제 전송 수. 빈 입력이어도 flush합니다.
    raise NotImplementedError("Q11 relay")
