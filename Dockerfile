FROM python:3.12-slim
WORKDIR /app
COPY app.py ./
COPY web ./web
COPY docs/sample.html ./docs/sample.html
ENV HOST=0.0.0.0 PORT=8000 PYTHONDONTWRITEBYTECODE=1 TOMBSTONE_CHECK_ORIGINS=0
USER 65534
EXPOSE 8000
CMD ["python", "app.py"]
