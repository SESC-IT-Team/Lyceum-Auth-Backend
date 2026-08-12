FROM python:3.13.14-alpine

WORKDIR /app

# Install system dependencies using Alpine's package manager (apk)
RUN apk add --no-cache git curl bash

# Install uv and dependencies
RUN pip install --no-cache-dir uv
COPY pyproject.toml README.md ./
RUN uv sync --no-dev

# Copy application files and set permissions
COPY . .
RUN chmod +x entrypoint.sh

ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["bash", "./entrypoint.sh"]