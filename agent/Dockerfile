FROM python:3.13-slim

WORKDIR /agent
COPY requirements.txt /agent/

RUN pip install -r requirements.txt

COPY . /agent

WORKDIR /

CMD ["adk", "api_server", "--host", "0.0.0.0", "--port", "8100", "--allow_origins", "http://localhost:3000"]
