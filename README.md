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
