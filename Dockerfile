FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV LLM_PROVIDER=nim
ENV NIM_BASE_URL=https://integrate.api.nvidia.com/v1
ENV NIM_TIMEOUT=60

CMD ["python", "demo.py"]
