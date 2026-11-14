"""응시용 자가 점검 도구 (표준 라이브러리 + docker 명령만 사용)

응시용 폴더에서 실행:  python self_check.py q01      (q01 q03 q05 q06 q07 q08 q09 또는 all)
- 문제를 푼 '결과 상태'를 확인합니다. 명령 작성 형식(답안 파일)의 채점은 하지 않습니다.
- q03은 delivery-api-container 실행 중, q05는 compose up 상태, q06~q09는 Kafka 실행 중이어야 합니다.
- q02, q04, q10은 화면 출력/서술형이라 자동 점검 대상이 아닙니다.
- 이 파일의 코드에는 기대 결과값이 들어 있으니, 다 풀기 전에는 열어 보지 마세요.
"""
import json
import subprocess
import sys
import urllib.request
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMPOSE = ["docker", "compose", "-f", str(HERE / "kafka-docker" / "docker-compose.yml"), "exec", "-T", "kafka"]
BS = ["--bootstrap-server", "localhost:9092"]
score = {"pass": 0, "fail": 0}


def check(name, cond, hint=""):
    score["pass" if cond else "fail"] += 1
    print(("  [O] " if cond else "  [X] ") + name + ("" if cond else f"  -> {hint}"))


def run(args, timeout=60):
    p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    return p.stdout, p.returncode


def http(url):
    try:
        with urllib.request.urlopen(url, timeout=3) as r:
            return r.read().decode()
    except Exception as e:
        return f"<ERR {e}>"


def q01():
    base = HERE / "q01" / f"report_{date.today():%Y%m%d}"
    check("오늘 날짜 report 폴더 존재", base.is_dir(), f"{base.name} 없음: [1] DATE 줄을 확인")
    if not base.is_dir():
        return
    rd = lambda p: (base / p).read_text(encoding="utf-8") if (base / p).exists() else ""
    check("logs/error_unique.log", rd("logs/error_unique.log") == "[ERROR] Disk quota exceeded\n[ERROR] Payment timeout\n", "[5] 확인")
    check("logs/disk.log 4줄", rd("logs/disk.log").count("\n") == 4, "[4] 확인")
    check("logs/head.txt 3줄", rd("logs/head.txt").count("\n") == 3, "[6] 확인")
    check("backup/error_unique.log", (base / "backup" / "error_unique.log").exists(), "[7] 확인")
    check("level_1~3 README", all(rd(f"level_{i}/README.txt") == f"This is level_{i} directory.\n" for i in (1, 2, 3)), "[8] 확인")
    check("summary.txt 3줄", rd("summary.txt") == f"date: {date.today():%Y%m%d}\nerror_unique: 2\ndisk: 4\n", "[9] 확인 (재실행 시에도 3줄이어야 함)")
    check("perm.txt = -rwxr-x---", rd("perm.txt").strip() == "-rwxr-x---", "[10] 확인")


def q03():
    check("GET http://localhost:8000/", http("http://localhost:8000/") == "Hello, SSAFY Delivery!", "포트 매핑·host 설정 확인")
    s = http("http://localhost:8000/status")
    check("GET /status", s.startswith("{") and json.loads(s) == {"service": "delivery-api", "status": "ok"}, s[:80])


def q05():
    check("GET http://localhost:8081", "SSAFY Delivery Dashboard" in http("http://localhost:8081"), "ports / volumes 확인")
    out, _ = run(["docker", "ps", "--format", "{{.Names}}"])
    check("delivery-web, delivery-api 실행 중", "delivery-web" in out and "delivery-api" in out, "container_name 확인")


def q06():
    out, rc = run(COMPOSE + ["kafka-topics", "--describe", "--topic", "delivery-status"] + BS)
    check("delivery-status 파티션 3 / RF 1", "PartitionCount: 3" in out and "ReplicationFactor: 1" in out, out.strip()[:120] or "토픽 없음")
    vals = [int(t.split("=")[1]) for t in out.replace(",", " ").split() if t.startswith("retention.ms=")]
    check("retention.ms = 30분(또는 [8]-(D) 후 10분)", any(v in (30 * 60 * 1000, 10 * 60 * 1000) for v in vals), "[5] 확인")
    lst, _ = run(COMPOSE + ["kafka-topics", "--list"] + BS)
    check("delivery-temp 삭제됨", "delivery-temp" not in lst.split(), "[7] 확인")


def q07():
    out, _ = run(COMPOSE + ["kafka-get-offsets"] + BS + ["--topic", "order-events"])
    offs = [int(l.split(":")[2]) for l in out.split() if l.startswith("order-events:")]
    check("order-events 파티션 3개", len(offs) == 3, out.strip() or "토픽 없음")
    check("메시지 25개 이상(5 + 20)", sum(offs) >= 25, f"현재 {sum(offs)}개")
    check("2개 이상 파티션에 저장", sum(1 for o in offs if o) >= 2, "[6] 단계 확인")


def consume(topic, extra=()):
    out, _ = run(COMPOSE + ["kafka-console-consumer", "--topic", topic, "--from-beginning", "--timeout-ms", "8000",
                            "--group", f"self-check-{topic}-{date.today():%H%M%S}"] + list(extra) + BS, timeout=90)
    return [l for l in out.splitlines() if l.strip() and not l.startswith("Processed")]


def q08():
    rows = consume("region-orders", ["--property", "print.key=true", "--property", "print.partition=true"])
    parts = {}
    for r in rows:
        cols = r.split("\t")
        if len(cols) >= 3:
            parts.setdefault(cols[1], set()).add(cols[0])
    check("region-orders 메시지 9개", len(rows) == 9, f"{len(rows)}개 (두 번 실행 시에도 삭제 후 재생성이므로 9개)")
    check("키 3종이 각각 한 파티션에만", len(parts) == 3 and all(len(v) == 1 for v in parts.values()), str(parts))


def q09():
    rows = consume("clean-orders")
    check("clean-orders = COFFEE, TEA, LATTE, SANDWICH", rows == ["COFFEE", "TEA", "LATTE", "SANDWICH"], str(rows))


TASKS = {"q01": q01, "q03": q03, "q05": q05, "q06": q06, "q07": q07, "q08": q08, "q09": q09}

if __name__ == "__main__":
    targets = sys.argv[1:] or ["all"]
    if "all" in targets:
        targets = list(TASKS)
    for t in targets:
        if t not in TASKS:
            print(f"{t}: 자동 점검 대상이 아닙니다 ({', '.join(TASKS)})")
            continue
        print(f"[{t}]")
        try:
            TASKS[t]()
        except Exception as e:
            check(f"{t} 점검 중 예외", False, repr(e))
    print(f"\n결과: O {score['pass']}  X {score['fail']}")
