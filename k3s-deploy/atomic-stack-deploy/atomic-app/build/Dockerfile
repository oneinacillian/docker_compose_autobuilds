# Dockerfile for Atomic App
FROM node:18

# Set the working directory
RUN mkdir -p /app
WORKDIR /app

# Install PM2 globally
RUN npm install -g pm2

# Install Git and other dependencies
RUN apt-get update && apt-get install -y git vim curl

# Clone the repository
RUN git clone https://github.com/pinknetworkx/eosio-contract-api.git /app/eosio-contract-api

# Copy entrypoint script
COPY ./entrypoint.sh /app/

# Install dependencies
WORKDIR /app/eosio-contract-api
RUN yarn install

# Set permissions
RUN chmod +x /app/entrypoint.sh

# Switch back to app directory
WORKDIR /app

# Expose ports
EXPOSE 9000 9001 9010

ENTRYPOINT ["/app/entrypoint.sh"]
