FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY flask_metrics_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY flask_metrics_service ./flask_metrics_service

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "30", "flask_metrics_service.app:app"]
