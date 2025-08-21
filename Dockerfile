FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

RUN pip install gunicorn

ENV PORT=5000

EXPOSE 5000

CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:$PORT app:app"]