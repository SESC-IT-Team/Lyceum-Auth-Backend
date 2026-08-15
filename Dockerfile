FROM python:3.13.14-alpine

WORKDIR /app

RUN apk add --no-cache git curl bash

RUN pip install --no-cache-dir uv
COPY uv.lock pyproject.toml README.md ./
RUN uv sync --no-dev

COPY . .
RUN chmod +x entrypoint.sh

ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["bash", "./entrypoint.sh"]