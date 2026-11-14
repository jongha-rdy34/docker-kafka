from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def home():
    return "Hello, SSAFY Delivery!"


@app.route("/status")
def status():
    return jsonify({"service": "delivery-api", "status": "ok"})


if __name__ == "__main__":
    # [오류 수정] 컨테이너는 정상 실행되지만, 호스트에서 접속하면 응답이 오지 않습니다.
    app.run(host="0.0.0.0", port=5000)
