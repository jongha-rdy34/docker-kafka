#!/bin/sh
# Q01 컨테이너 안에서 실행하는 리눅스 로그 정리 스크립트
# 실행 위치: 응시용 폴더(q01의 상위 폴더)
#   docker run --rm -v "$(pwd)/q01:/lab" -w /lab alpine:3.20 sh run.sh
# ______ 를 채우고, [오류 수정] 표시가 있는 줄은 고치세요.
set -e

# [1] 오늘 날짜를 YYYYMMDD 형식으로 DATE 변수에 저장  [오류 수정] 아래 줄에 오류가 1개 있습니다.
DATE=$(date +%Y%m%d)
BASE="/lab/report_$DATE"

# [2] logs, backup 디렉토리를 상위 디렉토리까지 한 번에 생성 (이미 있어도 오류가 나면 안 됨)
mkdir -p "$BASE/logs" "$BASE/backup"

# [3] 대문자 ERROR가 들어간 줄만 error.log에 저장 (덮어쓰기)
grep "ERROR" data/server.log > "$BASE/logs/error.log"

# [4] 대소문자 구분 없이 disk가 들어간 줄을 disk.log에 저장
grep -i "disk" data/server.log > "$BASE/logs/disk.log"

# [5] error.log를 정렬한 뒤 중복을 제거하여 error_unique.log에 저장
sort "$BASE/logs/error.log" | uniq > "$BASE/logs/error_unique.log"

# [6] 원본 로그의 상위 3줄만 head.txt에 저장
head -n 3 data/server.log > "$BASE/logs/head.txt"

# [7] error_unique.log를 backup 디렉토리에 복사 (logs 쪽 원본은 그대로 남아야 함)
cp "$BASE/logs/error_unique.log" "$BASE/backup/"

# [8] level_1 ~ level_3 디렉토리를 만들고 각 README.txt에 "This is level_X directory." 저장
for i in 1 2 3
do
    mkdir -p "$BASE/level_$i"
    echo "This is level_$i directory." > "$BASE/level_$i/README.txt"
done

# [9] summary.txt 작성: 첫 줄은 새로 쓰고(기존 내용 제거), 나머지 줄은 이어 붙임
echo "date: $DATE" > "$BASE/summary.txt"
echo "error_unique: $(wc -l < "$BASE/logs/error_unique.log")" >> "$BASE/summary.txt"
echo "disk: $(wc -l < "$BASE/logs/disk.log")" >> "$BASE/summary.txt"

# [10] deploy.sh에 "소유자 rwx / 그룹 r-x / 기타 권한 없음"을 숫자 방식으로 부여
#      (권한 실습은 컨테이너 내부 /tmp에서 진행하고 결과만 /lab에 저장)
mkdir -p /tmp/deploy
echo 'echo deploy ok' > /tmp/deploy/deploy.sh
chmod 750 /tmp/deploy/deploy.sh
ls -l /tmp/deploy/deploy.sh | cut -c1-10 > "$BASE/perm.txt"
/tmp/deploy/deploy.sh > "$BASE/deploy_result.txt"

# [11] 결과 확인
ls -R "$BASE"
cat "$BASE/summary.txt"
