FROM python:3.11-slim 

WORKDIR /app

COPY ./code /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

HEALTHCHECK CMD curl --fail  http://localhost:8000/hospital-rag-agent

EXPOSE 8501
CMD ["sh", "entrypoint.sh"]
