FROM python:3.11 as build

COPY main.py requirements.txt ./
COPY exporter ./app/exporter
COPY VERSION.txt ./app/exporter/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir ./app/exporter

FROM gcr.io/distroless/python3-debian11

ENV PYTHONPATH /app
COPY main.py /
COPY --from=build /usr/local/lib/python3.11/site-packages /app/

ENTRYPOINT ["python", "main.py"]
