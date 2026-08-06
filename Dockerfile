FROM python:3.13-slim

WORKDIR /src 

RUN apt-get update && apt-get install -y \
  gcc \
  libpq-dev \
  && rm -rf /var/lib/apt/lists/*

COPY ./src/matchpoint/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/matchpoint/ .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
