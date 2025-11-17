FROM python:3.11-slim

WORKDIR /app

COPY Backend/ /app/

RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["python", "app.py"]
