FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd -r -u 10001 signal && mkdir -p /data && chown signal:signal /data
COPY *.py /app/
COPY static /app/static
COPY tools /app/tools
USER signal
ENV HOST=0.0.0.0 PORT=8787 DATABASE_PATH=/data/signal_daily.db PYTHONUNBUFFERED=1
EXPOSE 8787
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python tools/healthcheck.py
CMD ["python", "production.py"]
