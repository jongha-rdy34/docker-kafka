⟪A:FROM⟫ python:3.10-slim
⟪A:WORKDIR⟫ /app
⟪A:COPY⟫ requirements.txt .
⟪A:RUN⟫ pip install --no-cache-dir -r requirements.txt
COPY ⟪A:app.py⟫ .
⟪A:CMD⟫ ["python", "app.py"]
