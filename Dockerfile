FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl bash && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir uv
COPY pyproject.toml README.md ./
RUN uv sync --no-dev

COPY . .
RUN chmod +x entrypoint.sh
ENV PYTHONPATH=/app
EXPOSE 8000
# CMD ["./entrypoint.sh"]
# CMD ["tail", "-f", "/dev/null"]
CMD ["bash", "./entrypoint.sh"]