# Project Deployment Documentation

## Introduction
This document provides detailed information about the deployment of our Dockerized services using Docker Compose. It includes configuration details and instructions for setting up and running Elasticsearch nodes, Kibana, Redis, RabbitMQ, Hyperion and Nodeos.

## Prerequisites
- Docker and Docker Compose installed on your machine.
- Basic understanding of Docker and containerization.
- Necessary environment variables set for `${ELASTICSEARCH_VERSION}`, `${KIBANA_VERSION}`, `${RABBITMQ_DEFAULT_USER}`, `${RABBITMQ_DEFAULT_PASS}`, `${RABBITMQ_DEFAULT_VHOST}`, and `${ENVIRONMENT}`. Please have a a look at the default.env file as an example and populate your .env.

## Services Overview
1. **Elasticsearch Nodes (es1, es2, es3):** 
   - Clustered Elasticsearch nodes for scalable search and analytics.
   - Custom JVM settings and cluster configurations.
   - Persistent volume bindings for data storage.
2. **Kibana:**
   - Web UI for visualizing and managing Elasticsearch data.
   - Configured to connect to the Elasticsearch cluster.
   - Health check integrated for service availability monitoring.
3. **Redis:**
   - In-memory data store, used as a database, cache, and message broker.
   - Append-only data persistence and LRU eviction policy.
   - Health check for ensuring service responsiveness.
4. **RabbitMQ:**
   - Open-source message broker for robust message queuing.
   - Management plugin enabled for easy monitoring.
   - Persistent volume for data and configurations.
5. **Hyperion (Custom Service):**
   - Custom service built with specific Dockerfile and environment settings.
   - Dependent on Elasticsearch (es1).
   - Port and volume configurations as per application requirements.
6. **Node (Custom Service):**
   - Another custom service with its unique configurations.
   - Also dependent on Elasticsearch (es1).

## Getting Started
1. Clone the repository and navigate to the project directory.
2. Ensure all environment variables are correctly set in your .env file.
3. Run `docker-compose up -d` to start all the services in detached mode.
4. Access Kibana at `http://localhost:5601` to visualize Elasticsearch data.
5. Check the status of all services using `docker-compose ps`.

## Additional Information
- **Configuration Adjustments:** Make any necessary changes to the `.yml` file to suit your environment.
- **Port Conflicts:** Ensure no conflicts with existing services running on the same ports.
- **Data Persistence:** Data volumes are set up for persistence. Adjust volume bindings as necessary.

## Troubleshooting
- If a service fails to start, check the Docker logs for that container for more information

## Environment Configuration
To properly configure the services, you need to set up the environment variables. Create a `.env` file in the root of the project directory with the following content:

```env
ELASTICSEARCH_VERSION=8.11.4
KIBANA_VERSION=8.11.4
RABBITMQ_DEFAULT_USER=rabbitmquser
RABBITMQ_DEFAULT_PASS=rabbitmqpass
RABBITMQ_DEFAULT_VHOST=hyperion
ENVIRONMENT=testnet
```


### Explanation of Variables

- `ELASTICSEARCH_VERSION`: Specifies the version of Elasticsearch to be used in the services.
- `KIBANA_VERSION`: Defines the version of Kibana for compatibility with Elasticsearch.
- `RABBITMQ_DEFAULT_USER`: The default username for RabbitMQ access.
- `RABBITMQ_DEFAULT_PASS`: The password for the RabbitMQ user.
- `RABBITMQ_DEFAULT_VHOST`: The default virtual host in RabbitMQ, used for isolation and management of queues.
- `ENVIRONMENT`: Indicates the environment setting, which can be adjusted based on the deployment stage (e.g., testnet, mainnet).

### Setting up the .env File

1. Copy the above content into a new file named `.env` in the same directory as your `docker-compose.yml`.
2. Adjust the values as needed to fit your specific environment or version requirements.
3. Ensure that the `.env` file is not committed to version control if it contains sensitive information (add `.env` to your `.gitignore` file).

By configuring these environment variables, the Docker Compose services will automatically use them during the deployment process. This setup ensures easy management and configuration of your services.