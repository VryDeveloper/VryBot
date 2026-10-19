FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY vrybot ./vrybot
COPY personas ./personas

# Run as a non-root user; /app/data holds the SQLite memory when enabled.
RUN useradd --create-home bot && mkdir -p /app/data && chown -R bot /app/data
USER bot

CMD ["python", "-m", "vrybot"]
