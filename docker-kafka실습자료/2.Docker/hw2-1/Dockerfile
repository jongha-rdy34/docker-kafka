FROM python:3.10-slim
______ /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
______ app.py .
CMD ["python", "app.py"]