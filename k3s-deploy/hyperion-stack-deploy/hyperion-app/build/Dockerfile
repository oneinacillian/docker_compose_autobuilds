# Dockerfile
FROM node:20

# Set the working directory
RUN mkdir -p /app
WORKDIR /app

# Install PM2 globally
RUN npm install -g pm2

# Install Git
RUN apt-get update && apt-get install -y git vim

# Clone the repository
RUN git clone -b v3.3.10-1 https://github.com/eosrio/hyperion-history-api.git /app

COPY ./entrypoint.sh .

# Install dependencies
RUN npm install

RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]