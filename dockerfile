FROM python:3.12-slim-bookworm

# Set working directory
WORKDIR /app

# Install system dependencies including build tools for insightface
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    build-essential \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

COPY pyproject.toml uv.lock /app/

RUN uv sync --locked

COPY setup.py constants.py /app/

RUN uv run setup.py

COPY . .

EXPOSE 80

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:80"]