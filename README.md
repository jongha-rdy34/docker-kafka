# docker-kafka

### 각 디렉토리 구성
#### n. Title 예) 1. Linux
- ws n-i : 실습에 필요한 파일들이 담긴 디렉토리 내부에 dockerfile, app.py, txt파일, ipynb 등이 들어있음  
- ws n-i.md : 실습 n-1부터 n-5번까지 문제 요구 사항  
  
#### n. Title_answer 예) 1. Linux_answer
- ws n-i.md : 4.Pro-Con을 제외한 파일들에는 터미널에 입력해야하는 커멘드가 들어있다.  
- 4.Pro-Con은 ipynb 기반 빈칸 채우기기 때문에 참고하면서 빈칸을 채워보면 된다  
  
### 주의사항
- 정답 코드는 내가 실습하면서 작성한거기 때문에, 틀린게 있을 수도 있다. 그래도 직접 결과 보면서 맞는 코드들만 담아둠.
- vscode에서 wsl 환경에 clone해서 풀어보셈
- 3.Kafka의 answer 코드들은 local에서 접근하는 방식으로 되어있다, 시험 요구사항은 docker 기반이기에, lab.ssafy에 올라온 de 실습 기반으로 zookeeper, kafka가 모두 들어있는 docker-compose.yml을 띄워놓고 거기에서 docker compose exec기반으로 .sh를 지워서 커맨드를 입력할 것.  


---

## Docker로 Kafka 실습하기 (최상단 `docker-compose.yml`)

ZooKeeper 없이 KRaft 모드로 동작하는 Kafka(`confluentinc/cp-kafka:7.6.1`)를 이 저장소 최상단의 `docker-compose.yml` 하나로 띄웁니다.
`3.Kafka`, `4.Pro-Con` 실습을 모두 이 파일로 풀 수 있습니다(ZooKeeper를 직접 띄우는 부분만 제외).
시험 공지대로 모든 명령은 `docker compose exec kafka ...` 형태로 입력합니다.

### 준비
- Docker Desktop 실행 + Settings → Resources → WSL integration에서 사용하는 Ubuntu를 켭니다. WSL에서 `docker ps`가 되면 준비 완료.
- Python 실습(`4.Pro-Con`)은 `pip install kafka-python==2.0.4` (Ubuntu 24.04는 venv 권장: `python3 -m venv .venv && source .venv/bin/activate`).

### 실행 모드

| 모드 | 명령 (저장소 최상단에서) | 브로커 | 사용 실습 |
|---|---|---|---|
| 기본 | `docker compose up -d` | `kafka`(id 1, localhost:9092) | ws3-2 ~ ws3-4, hw3-1, hw3-2, ws4-1 ~ ws4-5, hw4-1, hw4-2 |
| 클러스터 | `docker compose --profile cluster up -d` | `kafka`(9092), `kafka-2`(id 2, 9093), `kafka-3`(id 3, 9094) | ws3-5 |

```bash
docker compose up -d                                                            # 실행 (첫 실행 후 10~20초 기다리기)
docker compose ps                                                               # STATUS 확인 (controller, kafka 가 running)
docker compose exec kafka kafka-topics --list --bootstrap-server localhost:9092 # 오류 없이 끝나면 준비 완료
docker compose --profile cluster down                                           # 종료 (볼륨이 없어 토픽·메시지도 삭제됨)
```

### 명령 바꾸는 규칙
- `bin/kafka-topics.sh ...` → `docker compose exec kafka kafka-topics ...` (`bin/`과 `.sh`를 지움)
- 예: `docker compose exec kafka kafka-topics --create --topic test3-topic --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1`
- 토픽 설정 변경은 `kafka-configs`: `docker compose exec kafka kafka-configs --alter --topic test3-topic --bootstrap-server localhost:9092 --add-config retention.ms=600000`
- 콘솔 프로듀서·컨슈머는 터미널에서 직접 입력하고 `Ctrl+C`로 종료합니다.
- Python 노트북은 코드에 있는 `bootstrap_servers="localhost:9092"` 그대로 실행하면 됩니다.

### 실습별 대응

| 실습 | 방법 |
|---|---|
| ws3-1 | Java·ZooKeeper 설치는 해당 없음. `docker compose up -d` 후 `kafka-topics --list` 가 되는지 확인 |
| ws3-2 | 브로커 실행/종료 → `docker compose up -d` / `docker compose down`, 프로세스 확인(`pgrep`, `ps -fp`) → `docker compose ps`. list·describe는 그대로 |
| ws3-3, ws3-4, hw3-1 | 위 규칙대로 그대로 |
| hw3-2 | 그대로. 배치 크기 옵션은 `--producer-property batch.size=512`. `large_message.txt` 의 줄을 붙여 넣어 전송 |
| ws3-5 | 아래 "브로커 3대 실습" 참고 |
| ws4-*, hw4-* | 기본 모드로 띄우고 노트북 실행 |

### 브로커 3대 실습 (ws3-5)

설정 파일 복사(`server-1.properties` 등)와 브로커 3개 실행은 `--profile cluster` 가 대신합니다.

```bash
docker compose --profile cluster up -d
docker compose exec kafka   kafka-topics --list --bootstrap-server localhost:9092
docker compose exec kafka-2 kafka-topics --list --bootstrap-server localhost:9093
docker compose exec kafka-3 kafka-topics --list --bootstrap-server localhost:9094

docker compose exec kafka kafka-topics --create --topic test5-topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 3
docker compose exec kafka kafka-topics --describe --topic test5-topic --bootstrap-server localhost:9092
docker compose exec kafka kafka-console-producer --topic test5-topic --bootstrap-server localhost:9092
docker compose exec kafka kafka-console-consumer --topic test5-topic --from-beginning --bootstrap-server localhost:9092
```

리더 브로커 중단 (`jps`, `kill -9 ...` 대신). describe 결과의 `Leader` 번호에 맞는 서비스를 멈춥니다.

| Leader | 멈출 서비스 | 이후 명령을 보낼 서비스·주소 |
|---|---|---|
| 1 | `docker compose stop kafka` | `docker compose exec kafka-2 ... --bootstrap-server localhost:9093` |
| 2 | `docker compose stop kafka-2` | `docker compose exec kafka ... --bootstrap-server localhost:9092` (또는 kafka-3 / 9094) |
| 3 | `docker compose stop kafka-3` | `docker compose exec kafka ... --bootstrap-server localhost:9092` (또는 kafka-2 / 9093) |

```bash
# 예: Leader 가 2 인 경우
docker compose stop kafka-2
docker compose exec kafka kafka-topics --describe --topic test5-topic --bootstrap-server localhost:9092   # Isr 에서 2가 빠지고 새 Leader 선출
docker compose exec kafka kafka-console-consumer --topic test5-topic --bootstrap-server localhost:9093 --from-beginning   # 남은 브로커로 메시지 확인
docker compose start kafka-2                                                                              # 다시 켜면 Isr 복귀
```

- **`controller` 서비스는 멈추지 마세요.** KRaft 컨트롤러라서 멈추면 브로커 전체가 동작하지 않습니다.
- 확인한 결과(2026-11-07): Leader 2 중단 → `Leader: 3, Isr: 3,1`, 메시지 2개 그대로 조회, 2번 재시작 → `Isr: 3,1,2`.

### 알아 둘 점
- **첫 메시지 유실**: 토픽을 만들지 않고 바로 보내면(ws4-2) 토픽이 자동으로 만들어지면서 첫 메시지가 사라질 수 있습니다(kafka-python 기본 `retries=0`). 토픽을 먼저 만들어 두면 안전합니다.
- **처음 실행하는 컨슈머는 몇 초 늦게** 메시지를 받습니다(컨슈머 그룹용 내부 토픽 생성). 바로 안 나와도 잠시 기다리세요.
- **같은 `group_id` 로 다시 실행**하면 커밋된 위치부터 읽어서 아무것도 안 나올 수 있습니다. 처음부터 다시 보려면 group_id를 바꾸세요.
- **ws4-4**: 컨슈머 2개를 먼저 실행한 뒤 프로듀서를 실행해야 파티션이 나뉘어 소비되는 것을 볼 수 있습니다. 메시지를 먼저 보내 두면 먼저 들어온 컨슈머가 다 읽을 수 있습니다.
- **포트 9092·9093·9094 사용**: 시험용 `~/kafka-docker` 등 다른 Kafka와 동시에 띄우지 마세요(한쪽을 `down` 후 실행).
- 메모리 절약을 위해 브로커 힙을 512MB로 제한했습니다.
