import time

LOG_PATH = "/logs/order.log"   # 컨테이너 안에서 읽을 로그 파일 경로 (수정 금지)

with open(LOG_PATH, "r") as f:
    f.seek(0, 2)                # 파일 끝으로 이동: 실행 이후 새로 추가되는 줄만 읽음
    print("Watching order log...", flush=True)
    while True:
        line = f.readline()
        if line:
            line = line.strip()
            if "FAIL" in line:
                print("[ALERT] " + line, flush=True)
            else:
                print("[LOG] " + line, flush=True)
        else:
            time.sleep(1)
