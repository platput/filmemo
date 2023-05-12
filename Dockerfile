FROM python:3.11-slim

WORKDIR /app
COPY api/ /app/
RUN apt update && apt install -y build-essential

RUN pip install poetry
RUN poetry install

WORKDIR /app/api
# poetry run uvicorn api.main:app --host 0.0.0.0 --port 8081
CMD ["poetry", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
