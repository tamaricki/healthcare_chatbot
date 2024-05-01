FROM python:3.11-slim

WORKDIR /app

COPY ./code /app

COPY requirements.txt ./
RUN pip install -r requirements.txt 

EXPOSE 8000
CMD ["sh","entrypoint.sh"]