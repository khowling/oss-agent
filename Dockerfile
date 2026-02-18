FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY mcp-servers/ ./mcp-servers/

WORKDIR /app/src

EXPOSE 8080

CMD ["python", "main.py"]
