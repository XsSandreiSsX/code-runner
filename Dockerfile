FROM python:3.12-slim AS python-builder
RUN pip install poetry
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-root --only main


FROM python:3.12-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


COPY --from=python-builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=python-builder /usr/local/bin /usr/local/bin
COPY shared ./shared


FROM base AS main
COPY app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


FROM base AS worker

RUN apt-get update && apt-get install -y --no-install-recommends \
    libprotobuf32 libnl-route-3-200 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=xssandreissx/nsjail:latest /bin/nsjail /bin/nsjail

COPY worker ./worker

RUN mkdir -p /app/sandbox/rootfs /app/sandbox/runs && \
    cp -a /bin /app/sandbox/rootfs/ && \
    cp -a /lib /app/sandbox/rootfs/ && \
    cp -a /lib64 /app/sandbox/rootfs/ && \
    cp -a /usr /app/sandbox/rootfs/

RUN chown -R 1000:1000 /app/sandbox

CMD ["python", "-m", "worker.test"]