FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install pytest

COPY shqaff/ shqaff/
COPY tests/ tests/
COPY main.py .

CMD ["pytest", "tests/"]
