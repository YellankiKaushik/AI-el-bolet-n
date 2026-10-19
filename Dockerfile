FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN useradd -r -u 10001 signal && mkdir -p /data && chown -R signal:signal /app /data
USER signal
ENV HOST=0.0.0.0 PORT=8787 DATABASE_PATH=/data/signal_daily.db PYTHONUNBUFFERED=1
EXPOSE 8787
CMD ["python", "run.py"]
