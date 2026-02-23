FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code
COPY requirements.txt /code/

RUN pip install --no-cache-dir -r requirements.txt

# Install pre-trained models here
RUN python -c 'from sentence_transformers import SentenceTransformer; SentenceTransformer("all-MiniLM-L6-v2");'
RUN python -c 'from transformers import RobertaTokenizer, RobertaModel, RobertaConfig; RobertaTokenizer.from_pretrained("microsoft/unixcoder-base");'

COPY . /code

CMD uvicorn code_search.service:app --host 0.0.0.0 --workers ${WORKERS:-1}
