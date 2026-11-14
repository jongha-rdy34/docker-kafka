from flask import Flask
app = Flask(__name__)

@app.get("/")
def home():
    return "Parcel Hub Ready\n"

if __name__ == "__main__":
    # Q02: 컨테이너 밖에서 접속할 수 있도록 바인딩 오류를 수정하세요.
    app.run(host="127.0.0.1", port=5000)
