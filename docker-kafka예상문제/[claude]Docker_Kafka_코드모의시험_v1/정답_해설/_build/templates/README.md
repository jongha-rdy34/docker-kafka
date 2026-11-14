# 응시 안내 (환경 준비·실행·제출)

## 1. 환경 (가정 포함)

| 항목 | 이 모의시험의 기준 | 비고 |
|---|---|---|
| OS | WSL2 Ubuntu (VS Code에서 WSL로 열기) | 실습자료 README 기준 |
| Docker | Docker Engine + Compose v2 (`docker compose`) | `docker-compose`(v1) 아님 |
| Kafka | `kafka-docker/docker-compose.yml` (cp-kafka 7.6.1, KRaft 단일 브로커, 서비스 `kafka`, 9092) | **[가정]** 공지의 Setup.exe가 만드는 파일과 같은 조건으로 만든 대체 파일 |
| Python | 3.10 이상 + `kafka-python==2.0.4` + Jupyter(VS Code 노트북) | 치트시트 기준 버전 |
| 사용 이미지 | `alpine:3.20`, `alpine`, `hello-world`, `python:3.10-slim`, `nginx:alpine`, `confluentinc/cp-kafka:7.6.1` | 처음 실행 시 자동 다운로드 |
| 사용 포트 | 8000(Q03), 8081(Q05), 9092(Kafka) | 다른 프로그램이 쓰고 있으면 먼저 종료 |

> 실제 시험 PC의 폴더 위치는 `~/kafka-docker` 입니다(공지). 이 모의시험에서는 같은 역할을 하는 `응시용/kafka-docker` 를 씁니다.

## 2. 시작 전 준비 (시간 측정 전)

```bash
# 응시용 폴더를 WSL에서 연 상태
pip install kafka-python==2.0.4
docker pull alpine:3.20
docker pull python:3.10-slim
docker pull nginx:alpine
docker pull confluentinc/cp-kafka:7.6.1

cd kafka-docker
docker compose up -d
docker compose exec kafka kafka-topics --list --bootstrap-server localhost:9092   # 오류 없이 끝나면 준비 완료(처음엔 빈 목록)
cd ..
```

- `q01/run.sh` 는 줄바꿈이 LF여야 합니다. Windows 편집기에서 CRLF로 바뀌면 `sh: ... not found` 류 오류가 납니다.
- 노트북은 각 셀을 위에서부터 순서대로 실행합니다.

## 3. 진행 방법

1. `문제지.md` 를 읽고 각 문항 폴더의 파일을 수정합니다.
2. 명령 답안(`qNN_answer.txt`)은 실제로 터미널에 입력해 결과를 확인한 뒤 적습니다.
3. 결과 상태 점검: `python self_check.py q01` (또는 `all`). Q02·Q04·Q10은 자동 점검 대상이 아닙니다.
4. 다 풀었으면 `../정답_해설/정답해설.md` 로 채점합니다.

## 4. 제출 규칙 (연습용 가정)

- 지정한 파일만 수정, 파일 이름 유지, 실행을 막는 미완성 코드는 남기지 않습니다.
- 빈칸 `______` 가 남아 있으면 해당 빈칸은 0점으로 처리합니다.
- 실행 결과물(`q01/report_*`, 컨테이너, 토픽)은 제출 대상이 아닙니다. 응시용 폴더 전체를 압축해 제출하는 상황을 가정합니다.

## 5. 정리

```bash
docker rm -f delivery-api-container order-watcher-c 2>/dev/null
(cd q05 && docker compose down)
(cd kafka-docker && docker compose down)      # 이 Compose는 볼륨이 없어 down 하면 토픽·메시지도 함께 사라짐
```
