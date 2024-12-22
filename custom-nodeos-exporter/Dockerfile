FROM python:3.9-slim
RUN apt-get update && apt-get upgrade && apt-get install curl -y
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "nodeos_exporter.py"]