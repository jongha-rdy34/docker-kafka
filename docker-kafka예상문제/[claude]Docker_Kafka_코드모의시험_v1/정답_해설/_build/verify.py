"""정답(정답_해설)을 실제 Docker / Kafka 위에서 실행해 검증하고, 응시용의 버그가 실제로 오류를 내는지도 확인한다.

사용: python verify.py <kafka-python 이 설치된 python 경로> [q01 q03 ...]
- 정답_해설 을 임시 폴더로 복사해서 실행하므로 원본은 바뀌지 않는다.
- 대화형(-it, 콘솔 프로듀서 입력)은 같은 의미의 비대화형 명령(-dit + exec, exec -T < 파일)으로 대체한다.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ANS = HERE.parent
EXAM = ANS.parent / "응시용"
PY = sys.argv[1] if len(sys.argv) > 1 else sys.executable
ONLY = set(sys.argv[2:])
WORK = Path(tempfile.mkdtemp(prefix="dkv_"))
RESULTS = []


def sh(cmd, cwd=None, input=None, check=False, timeout=180):
    p = subprocess.run(cmd, cwd=cwd, input=input, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=timeout, shell=isinstance(cmd, str))
    if check and p.returncode != 0:
        raise RuntimeError(f"FAILED {cmd}\n{p.stdout}\n{p.stderr}")
    return p


def ok(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  :: {detail}"), flush=True)


def http_get(url, tries=20):
    for _ in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=3) as r:
                return r.read().decode()
        except Exception as e:
            last = e
            time.sleep(1)
    return f"<ERR {last}>"


def selfcheck(*qs):
    """정답 복사본의 self_check.py 실행 결과가 모두 O 인지"""
    r = sh([sys.executable, "-X", "utf8", str(WORK / "ans" / "self_check.py")] + list(qs), timeout=300)
    good = "X 0" in r.stdout and "[X]" not in r.stdout
    ok("SELF_CHECK " + " ".join(qs), good, r.stdout[-600:])


def want(q):
    return not ONLY or q in ONLY


def copy_tree():
    for sub in ANS.iterdir():
        if sub.name == "_build" or (sub.is_file() and sub.name != "self_check.py"):
            continue
        (WORK / "ans").mkdir(parents=True, exist_ok=True)
        if sub.is_file():
            shutil.copy(sub, WORK / "ans" / sub.name)
        else:
            shutil.copytree(sub, WORK / "ans" / sub.name)
    shutil.copytree(EXAM, WORK / "exam")


def vol(p: Path):
    return p.as_posix()


# ---------------------------------------------------------------- Q01
def q01():
    lab = WORK / "ans" / "q01"
    cmd = ["docker", "run", "--rm", "-v", f"{vol(lab)}:/lab", "-w", "/lab", "alpine:3.20", "sh", "run.sh"]
    r1 = sh(cmd)
    r2 = sh(cmd)  # 재실행해도 결과가 같아야 함
    ok("Q01 정답 스크립트 2회 실행 성공", r1.returncode == 0 and r2.returncode == 0, r1.stderr + r2.stderr)
    base = lab / f"report_{date.today():%Y%m%d}"
    rd = lambda p: (base / p).read_text(encoding="utf-8")
    ok("Q01 error.log 4줄", rd("logs/error.log").count("\n") == 4, rd("logs/error.log"))
    ok("Q01 error_unique.log 2줄(정렬·중복제거)",
       rd("logs/error_unique.log") == "[ERROR] Disk quota exceeded\n[ERROR] Payment timeout\n", rd("logs/error_unique.log"))
    ok("Q01 disk.log 4줄(-i)", rd("logs/disk.log").count("\n") == 4, rd("logs/disk.log"))
    ok("Q01 head.txt 3줄", rd("logs/head.txt").splitlines() ==
       ["[INFO] Delivery server start", "[ERROR] Disk quota exceeded", "[WARNING] Memory usage 85%"])
    ok("Q01 backup 복사", (base / "backup/error_unique.log").exists() and (base / "logs/error_unique.log").exists())
    ok("Q01 level README", all(rd(f"level_{i}/README.txt") == f"This is level_{i} directory.\n" for i in (1, 2, 3)))
    ok("Q01 summary 3줄(재실행 후에도)", rd("summary.txt") == f"date: {date.today():%Y%m%d}\nerror_unique: 2\ndisk: 4\n", rd("summary.txt"))
    ok("Q01 perm.txt", rd("perm.txt").strip() == "-rwxr-x---", rd("perm.txt"))
    ok("Q01 deploy 실행", rd("deploy_result.txt").strip() == "deploy ok")
    selfcheck("q01")
    print("    stdout 마지막:", r2.stdout.strip().splitlines()[-3:])
    # 응시용 버그 줄(DATE = ...) 확인: 빈칸 줄은 주석 처리 후 버그 줄만 남겨 실행
    buggy = (WORK / "exam" / "q01" / "run.sh").read_text(encoding="utf-8").splitlines()
    head = [l for l in buggy[:12]]
    tmp = WORK / "q01bug"
    tmp.mkdir()
    (tmp / "run.sh").write_text("\n".join(head) + "\necho reached\n", encoding="utf-8", newline="\n")
    rb = sh(["docker", "run", "--rm", "-v", f"{vol(tmp)}:/lab", "-w", "/lab", "alpine:3.20", "sh", "run.sh"])
    ok("Q01 응시용 'DATE = ...' 는 오류로 중단", rb.returncode != 0 and "reached" not in rb.stdout, rb.stdout + rb.stderr)
    print("    버그 오류 메시지:", rb.stderr.strip())


# ---------------------------------------------------------------- Q02
def q02():
    sh("docker rm -f hello-test devbox")
    r = sh(["docker", "run", "--name", "hello-test", "hello-world"])
    ok("Q02 hello-world 실행", "Hello from Docker!" in r.stdout, r.stdout[:200])
    r = sh(["docker", "ps", "-a", "--filter", "name=hello-test", "--format", "{{.Names}} {{.Status}}"])
    ok("Q02 ps -a 에 Exited 표시", "hello-test Exited" in r.stdout, r.stdout)
    ok("Q02 rm", sh(["docker", "rm", "hello-test"]).returncode == 0)
    ok("Q02 images", "hello-world" in sh(["docker", "images"]).stdout)
    # -it bash 를 비대화형으로 대체: -dit 로 띄우고 exec 로 같은 작업
    sh(["docker", "run", "-dit", "--name", "devbox", "python:3.10-slim", "bash"], check=True)
    pwd = sh(["docker", "exec", "devbox", "pwd"]).stdout.strip()
    sh(["docker", "exec", "devbox", "sh", "-c", 'echo "inside devbox" > note.txt'], check=True)
    py = sh(["docker", "exec", "devbox", "python", "-c", "print(6 * 7)"]).stdout.strip()
    sh(["docker", "stop", "devbox"], check=True)
    st = sh(["docker", "ps", "-a", "--filter", "name=devbox", "--format", "{{.Status}}"]).stdout
    sh(["docker", "start", "devbox"], check=True)
    note = sh(["docker", "exec", "devbox", "cat", "note.txt"]).stdout.strip()
    ok("Q02 devbox pwd=/ , 42, 재시작 후 note 유지", pwd == "/" and py == "42" and note == "inside devbox" and "Exited" in st,
       f"{pwd} {py} {note} {st}")
    sh("docker stop devbox"); sh("docker rm devbox")
    sh(["docker", "run", "-dit", "--name", "devbox", "python:3.10-slim", "bash"], check=True)
    r = sh(["docker", "exec", "devbox", "cat", "note.txt"])
    ok("Q02 rm 후 새 run 에는 note.txt 없음", r.returncode != 0, r.stdout)
    sh("docker rm -f devbox")


# ---------------------------------------------------------------- Q03
def q03():
    d = WORK / "ans" / "q03"
    sh("docker rm -f delivery-api-container")
    r = sh(["docker", "build", "-t", "delivery-api", "."], cwd=d, timeout=600)
    ok("Q03 정답 빌드", r.returncode == 0, r.stderr[-500:])
    sh(["docker", "run", "-d", "-p", "8000:5000", "--name", "delivery-api-container", "delivery-api"], check=True)
    home = http_get("http://localhost:8000/")
    st = http_get("http://localhost:8000/status")
    ok("Q03 GET /", home == "Hello, SSAFY Delivery!", home)
    ok("Q03 GET /status", json.loads(st) == {"service": "delivery-api", "status": "ok"} if st.startswith("{") else False, st)
    selfcheck("q03")
    sh("docker stop delivery-api-container"); sh("docker rm delivery-api-container")
    # 버그 app.py (host 미지정) 로 빌드하면 컨테이너는 Up 이지만 응답 없음
    b = WORK / "q03bug"
    shutil.copytree(d, b)
    shutil.copy(WORK / "exam" / "q03" / "app.py", b / "app.py")
    sh(["docker", "build", "-t", "delivery-api-bug", "."], cwd=b, check=True, timeout=600)
    sh(["docker", "run", "-d", "-p", "8000:5000", "--name", "delivery-api-bug", "delivery-api-bug"], check=True)
    time.sleep(4)
    up = sh(["docker", "ps", "--filter", "name=delivery-api-bug", "--format", "{{.Status}}"]).stdout
    res = http_get("http://localhost:8000/", tries=3)
    logs = sh(["docker", "logs", "delivery-api-bug"]).stderr
    ok("Q03 응시용 app.run(port=5000): 컨테이너 Up, 호스트 응답 없음", "Up" in up and res.startswith("<ERR"), f"{up} {res}")
    print("    버그 버전 로그:", [l for l in logs.splitlines() if "Running on" in l])
    sh("docker rm -f delivery-api-bug")


# ---------------------------------------------------------------- Q04
def q04():
    d = WORK / "ans" / "q04"
    sh("docker rm -f order-watcher-c order-watcher-bug")
    ok("Q04 정답 빌드", sh(["docker", "build", "-t", "order-watcher", "."], cwd=d, timeout=600).returncode == 0)
    # 포그라운드 대신 -d + docker logs 로 확인 (출력은 동일)
    sh(["docker", "run", "-d", "--name", "order-watcher-c", "-v", f"{vol(d / 'order.log')}:/logs/order.log", "order-watcher"], check=True)
    time.sleep(3)
    with open(d / "order.log", "a", encoding="utf-8", newline="\n") as f:   # echo ... >> order.log 와 같음
        f.write("[OK] order-101 delivered\n")
        f.write("[FAIL] order-102 address not found\n")
    time.sleep(4)
    logs = sh(["docker", "logs", "order-watcher-c"]).stdout
    ok("Q04 [LOG]/[ALERT] 출력", "[LOG] [OK] order-101 delivered" in logs and "[ALERT] [FAIL] order-102 address not found" in logs
       and "[INIT]" not in logs, logs)
    print("    logs:", logs.strip().splitlines())
    # > 로 덮어쓰면? (해설용 관찰)
    with open(d / "order.log", "w", encoding="utf-8", newline="\n") as f:
        f.write("[OK] order-103 delivered\n")
    time.sleep(4)
    logs2 = sh(["docker", "logs", "order-watcher-c"]).stdout
    print("    '>' 덮어쓰기 후 새 출력:", logs2.strip().splitlines()[len(logs.strip().splitlines()):])
    sh("docker rm -f order-watcher-c")
    # 버그 CMD
    b = WORK / "q04bug"
    shutil.copytree(WORK / "exam" / "q04", b)
    df = (d / "Dockerfile").read_text(encoding="utf-8").replace('CMD ["python", "watch_log.py"]', 'CMD ["python watch_log.py"]')
    (b / "Dockerfile").write_text(df, encoding="utf-8", newline="\n")
    rb = sh(["docker", "build", "-t", "order-watcher-bug", "."], cwd=b)
    rr = sh(["docker", "run", "--name", "order-watcher-bug", "-v", f"{vol(b / 'order.log')}:/logs/order.log", "order-watcher-bug"])
    ok("Q04 응시용 CMD [\"python watch_log.py\"]: 빌드 성공·실행 실패", rb.returncode == 0 and rr.returncode != 0, rr.stderr)
    print("    버그 실행 오류:", rr.stderr.strip()[-200:])
    sh("docker rm -f order-watcher-bug")


# ---------------------------------------------------------------- Q05
def q05():
    d = WORK / "ans" / "q05"
    sh("docker rm -f delivery-web delivery-api")
    r = sh("docker compose up -d", cwd=d, timeout=300)
    ok("Q05 compose up -d", r.returncode == 0, r.stderr[-400:])
    ps = sh("docker compose ps --format \"{{.Name}} {{.State}}\"", cwd=d).stdout
    ok("Q05 compose ps 두 컨테이너 running", "delivery-web running" in ps and "delivery-api running" in ps, ps)
    pg = sh("docker compose exec -T api ping -c 3 web", cwd=d)
    ok("Q05 ping -c 3 web", pg.returncode == 0 and "3 packets received" in pg.stdout, pg.stdout[-200:])
    sh("docker compose exec -T api apk add curl", cwd=d, timeout=300)
    c = sh("docker compose exec -T api curl -s http://web", cwd=d)
    ok("Q05 api→web curl", "SSAFY Delivery Dashboard" in c.stdout, c.stdout + c.stderr)
    h = http_get("http://localhost:8081")
    ok("Q05 호스트 8081", "SSAFY Delivery Dashboard" in h, h)
    bad = sh("docker compose exec -T api curl -s http://localhost:8081", cwd=d)
    ok("Q05 api 안에서 localhost:8081 은 실패", bad.returncode != 0, f"rc={bad.returncode} {bad.stdout}")
    print("    localhost:8081 rc:", bad.returncode)
    selfcheck("q05")
    sh("docker compose down", cwd=d, timeout=120)


# ---------------------------------------------------------------- Kafka
def kexec(args, cwd, input=None, timeout=120):
    return sh(["docker", "compose", "exec", "-T", "kafka"] + args, cwd=cwd, input=input, timeout=timeout)


BS = ["--bootstrap-server", "localhost:9092"]


def kafka_up():
    d = WORK / "ans" / "kafka-docker"
    sh("docker compose down -v", cwd=d, timeout=120)
    r = sh("docker compose up -d", cwd=d, timeout=600)
    ok("KAFKA compose up -d", r.returncode == 0, r.stderr[-400:])
    for _ in range(60):
        if kexec(["kafka-topics", "--list"] + BS, d).returncode == 0:
            break
        time.sleep(2)
    ps = sh("docker compose ps --format \"{{.Service}} {{.State}}\"", cwd=d).stdout
    ok("KAFKA 서비스 kafka running + --list 응답", "kafka running" in ps, ps)
    return d


def q06(d):
    r = kexec(["kafka-topics", "--create", "--topic", "delivery-status"] + BS + ["--partitions", "3", "--replication-factor", "1"], d)
    ok("Q06 create delivery-status", "Created topic delivery-status" in r.stdout, r.stdout + r.stderr)
    ok("Q06 list", "delivery-status" in kexec(["kafka-topics", "--list"] + BS, d).stdout)
    ds = kexec(["kafka-topics", "--describe", "--topic", "delivery-status"] + BS, d).stdout
    ok("Q06 describe PartitionCount: 3 / RF 1 / Leader 1", "PartitionCount: 3" in ds and "ReplicationFactor: 1" in ds and ds.count("Leader: 1") == 3, ds)
    print("    describe:\n      " + "\n      ".join(ds.strip().splitlines()))
    r = kexec(["kafka-configs", "--alter", "--topic", "delivery-status"] + BS + ["--add-config", "retention.ms=1800000"], d)
    ok("Q06 alter retention", r.returncode == 0, r.stdout + r.stderr)
    print("    alter:", r.stdout.strip())
    cf = kexec(["kafka-configs", "--describe", "--topic", "delivery-status"] + BS, d).stdout
    ok("Q06 describe configs retention.ms=1800000", "retention.ms=1800000" in cf, cf)
    print("    configs:", cf.strip())
    kexec(["kafka-topics", "--create", "--topic", "delivery-temp"] + BS + ["--partitions", "1", "--replication-factor", "1"], d)
    kexec(["kafka-topics", "--delete", "--topic", "delivery-temp"] + BS, d)
    time.sleep(2)
    ok("Q06 delivery-temp 삭제", "delivery-temp" not in kexec(["kafka-topics", "--list"] + BS, d).stdout)
    # 디버깅 원본 명령의 실제 반응
    a = sh(["docker", "compose", "exec", "-T", "kafka", "./bin/kafka-topics.sh", "--create", "--topic", "delivery-log"] + BS + ["--patitions", "2", "--replication-factor", "1"], cwd=d)
    a2 = kexec(["kafka-topics", "--create", "--topic", "delivery-log"] + BS + ["--patitions", "2", "--replication-factor", "1"], d)
    b = kexec(["kafka-topics", "--describe", "delivery-status"] + BS, d)
    c = kexec(["kafka-topics", "--create", "--topic", "delivery-replica"] + BS + ["--partitions", "1", "--replication-factor", "3"], d)
    dd = kexec(["kafka-topics", "--alter", "--topic", "delivery-status"] + BS + ["--add-config", "retention.ms=600000"], d)
    ok("Q06 (A) ./bin/kafka-topics.sh 실패", a.returncode != 0, a.stdout + a.stderr)
    ok("Q06 (A) --patitions 실패", a2.returncode != 0, a2.stdout + a2.stderr)
    ok("Q06 (C) RF 3 실패", c.returncode != 0 and "replication factor" in (c.stdout + c.stderr).lower(), c.stdout + c.stderr)
    ok("Q06 (D) kafka-topics --add-config 실패", dd.returncode != 0, dd.stdout + dd.stderr)
    first = lambda p: next((l for l in (p.stderr + p.stdout).splitlines() if l.strip()), "")
    print("    (A) .sh  :", first(a))
    print("    (A) typo :", first(a2))
    print("    (B) rc", b.returncode, ":", first(b), "| lines:", len(b.stdout.splitlines()))
    print("    (C)      :", [l for l in (c.stdout + c.stderr).splitlines() if "eplication" in l][:1])
    print("    (D)      :", first(dd))
    for name, fixed in [("A", ["kafka-topics", "--create", "--topic", "delivery-log"] + BS + ["--partitions", "2", "--replication-factor", "1"]),
                        ("B", ["kafka-topics", "--describe", "--topic", "delivery-status"] + BS),
                        ("C", ["kafka-topics", "--create", "--topic", "delivery-replica"] + BS + ["--partitions", "1", "--replication-factor", "1"]),
                        ("D", ["kafka-configs", "--alter", "--topic", "delivery-status"] + BS + ["--add-config", "retention.ms=600000"])]:
        ok(f"Q06 ({name}) 수정 명령 성공", kexec(fixed, d).returncode == 0)
    ok("Q06 (D) 후 retention.ms=600000", "retention.ms=600000" in kexec(["kafka-configs", "--describe", "--topic", "delivery-status"] + BS, d).stdout)


def offsets(d, topic):
    out = kexec(["kafka-get-offsets"] + BS + ["--topic", topic], d).stdout
    return {int(l.split(":")[1]): int(l.split(":")[2]) for l in out.split() if l.startswith(topic + ":")}


def q07(d):
    q = WORK / "ans" / "q07"
    kexec(["kafka-topics", "--create", "--topic", "order-events"] + BS + ["--partitions", "3", "--replication-factor", "1"], d)
    small = (q / "small_messages.txt").read_text(encoding="utf-8")
    kexec(["kafka-console-producer", "--topic", "order-events"] + BS, d, input=small)
    o1 = offsets(d, "order-events")
    ok("Q07 small 5개 저장", sum(o1.values()) == 5, o1)
    print("    small 후 offsets:", o1, "→ 한 파티션 집중" if max(o1.values()) == 5 else "→ 분산")
    allm = kexec(["kafka-console-consumer", "--topic", "order-events", "--from-beginning", "--timeout-ms", "8000"] + BS, d).stdout
    ok("Q07 --from-beginning 5개", len([l for l in allm.splitlines() if l.startswith("order-")]) == 5, allm)
    per = {}
    for p in range(3):
        out = kexec(["kafka-console-consumer", "--topic", "order-events"] + BS + ["--from-beginning", "--partition", str(p), "--timeout-ms", "6000"], d).stdout
        per[p] = len([l for l in out.splitlines() if l.startswith("order-")])
    ok("Q07 --partition 별 조회 합계 = offsets", per == o1, f"{per} vs {o1}")
    large = (q / "large_messages.txt").read_text(encoding="utf-8")
    kexec(["kafka-console-producer", "--topic", "order-events"] + BS + ["--producer-property", "batch.size=512"], d, input=large)
    o2 = offsets(d, "order-events")
    diff = {p: o2[p] - o1.get(p, 0) for p in o2}
    ok("Q07 large 20개 저장", sum(diff.values()) == 20, diff)
    ok("Q07 batch.size=512 에서 2개 이상 파티션 분산", sum(1 for v in diff.values() if v) >= 2, diff)
    print("    large 분포:", diff, "누적:", o2)
    # 비교: 같은 20개를 기본 batch.size 로 보내면?
    kexec(["kafka-topics", "--create", "--topic", "order-events-default"] + BS + ["--partitions", "3", "--replication-factor", "1"], d)
    kexec(["kafka-console-producer", "--topic", "order-events-default"] + BS, d, input=large)
    print("    (참고) 기본 batch.size 로 20개:", offsets(d, "order-events-default"))


def run_nb(path: Path):
    nb = json.loads(path.read_text(encoding="utf-8"))
    code = "\n\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
    script = WORK / (path.stem + "_run.py")
    script.write_text(code, encoding="utf-8")
    import os
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    p = subprocess.run([PY, "-I", "-X", "utf8", str(script)], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=120, env=env)
    return p


def q08():
    q = WORK / "ans" / "q08"
    r1 = run_nb(q / "q08_producer.ipynb")
    ok("Q08 producer 1회차", r1.returncode == 0, r1.stderr[-600:])
    r2 = run_nb(q / "q08_producer.ipynb")
    ok("Q08 producer 2회차(기존 토픽 삭제 경로)", r2.returncode == 0 and "삭제 완료" in r2.stdout, f"rc={r2.returncode} out={r2.stdout[:300]} err={r2.stderr[-300:]}")
    sent = re.findall(r"key=(\w+) -> partition (\d)", r2.stdout)
    pk = {}
    for k, p in sent:
        pk.setdefault(k, set()).add(p)
    ok("Q08 프로듀서 측: 키별 파티션 1개", len(sent) == 9 and all(len(v) == 1 for v in pk.values()), pk)
    ok("Q08 세 키가 서로 다른 파티션(seoul 0, daejeon 1, ulsan 2)",
       {k: sorted(v) for k, v in pk.items()} == {"seoul": ["0"], "daejeon": ["1"], "ulsan": ["2"]}, pk)
    print("    키→파티션:", {k: sorted(v) for k, v in pk.items()})
    c1 = run_nb(q / "q08_consumer.ipynb")
    ok("Q08 consumer 9건 + 3키 OK", c1.stdout.count("Received:") == 9 and c1.stdout.count(" OK") == 3 and "NG" not in c1.stdout, c1.stdout + c1.stderr[-400:])
    c2 = run_nb(q / "q08_consumer.ipynb")
    ok("Q08 같은 group 재실행 시 0건(커밋 위치부터)", c2.stdout.count("Received:") == 0, c2.stdout)
    # 응시용 버그(delete_topics(topic_name)) 는 토픽이 있을 때 오류
    src = (q / "q08_producer.ipynb").read_text(encoding="utf-8").replace(
        "admin_client.delete_topics([topic_name])", "admin_client.delete_topics(topic_name)")
    bug = WORK / "q08bug"; bug.mkdir()
    (bug / "q08_producer_bug.ipynb").write_text(src, encoding="utf-8")
    rb = run_nb(bug / "q08_producer_bug.ipynb")
    ok("Q08 응시용 delete_topics(topic_name) 은 2회차에 오류", rb.returncode != 0, rb.stdout[-300:])
    print("    버그 오류:", rb.stderr.strip().splitlines()[-1] if rb.stderr.strip() else "")


def q09():
    q = WORK / "ans" / "q09"
    # (1) 응시용 버그 먼저: value=transformed.encode() + value_serializer=str.encode → TypeError
    run_nb(q / "q09_1_input_producer.ipynb")
    src = (q / "q09_2_transformer.ipynb").read_text(encoding="utf-8")
    src = src.replace('value=transformed)', 'value=transformed.encode(\\"utf-8\\"))')
    src = src.replace('\\"transformer-group\\"', '\\"transformer-bug\\"')
    assert "transformer-bug" in src and "transformed.encode" in src
    bug = WORK / "q09bug"; bug.mkdir()
    (bug / "t.ipynb").write_text(src, encoding="utf-8")
    rb = run_nb(bug / "t.ipynb")
    ok("Q09 응시용 이중 인코딩은 TypeError", rb.returncode != 0 and "TypeError" in rb.stderr, rb.stderr[-300:])
    print("    버그 오류:", rb.stderr.strip().splitlines()[-1] if rb.stderr.strip() else "")
    # (2) 정답 순서대로 실행 (입력 토픽 재생성부터)
    r = run_nb(q / "q09_1_input_producer.ipynb")
    ok("Q09-1 입력 준비(토픽 삭제 후 재생성)", r.returncode == 0 and "삭제 완료" in r.stdout, r.stderr[-500:])
    t = run_nb(q / "q09_2_transformer.ipynb")
    ok("Q09-2 forwarded=4, Skipped 1", "forwarded=4" in t.stdout and t.stdout.count("Skipped empty message") == 1, t.stdout + t.stderr[-400:])
    o = run_nb(q / "q09_3_output_consumer.ipynb")
    ok("Q09-3 결과 [COFFEE, TEA, LATTE, SANDWICH]", "results: ['COFFEE', 'TEA', 'LATTE', 'SANDWICH'] count: 4" in o.stdout, o.stdout + o.stderr[-400:])
    print("    ", [l for l in o.stdout.splitlines() if l.startswith("results")])
    # (3) 같은 그룹 ID로 1→2→3 을 한 번 더: 토픽을 지우고 다시 만들면 이전 커밋 오프셋도 사라지는지
    run_nb(q / "q09_1_input_producer.ipynb")
    t2 = run_nb(q / "q09_2_transformer.ipynb")
    o2 = run_nb(q / "q09_3_output_consumer.ipynb")
    ok("Q09 전체 재실행(같은 그룹)도 forwarded=4 / count: 4", "forwarded=4" in t2.stdout and "count: 4" in o2.stdout, t2.stdout[-200:] + o2.stdout[-200:])


def main():
    copy_tree()
    print("WORK =", WORK)
    for q, f in [("q01", q01), ("q02", q02), ("q03", q03), ("q04", q04), ("q05", q05)]:
        if want(q):
            f()
    if any(want(q) for q in ("q06", "q07", "q08", "q09")):
        d = kafka_up()
        if want("q06"): q06(d)
        if want("q07"): q07(d)
        if want("q08"): q08()
        if want("q09"): q09()
        selfcheck(*[q for q in ("q06", "q07", "q08", "q09") if want(q)])
        sh("docker compose down -v", cwd=d, timeout=120)
    n = sum(1 for r in RESULTS if r[1])
    print(f"\n==== {n}/{len(RESULTS)} PASS ====")
    for name, good, detail in RESULTS:
        if not good:
            print("FAIL", name, detail[:300])


if __name__ == "__main__":
    main()
