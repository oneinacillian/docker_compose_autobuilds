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
   - Also dependent on Elasticsearch (es1).
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
   - Dependent on Elasticsearch (es1,es2,es3).
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

## Cleanup Process

We provide a `cleanup.sh` script to help with the clean and efficient removal of Docker resources used by this project. This script is particularly useful when you need to reset your environment or ensure that all resources are properly removed after testing or development.

### Script Contents

The `cleanup.sh` script performs the following actions:

1. **Stop All Services:**
   - Executes `docker-compose down` to stop all running containers managed by the `docker-compose.yml` file.

2. **Remove Docker Volumes:**
   - Identifies and removes specific Docker volumes associated with this project. The volumes targeted for removal are:
     - `node`
     - `esdata1`
     - `esdata2`
     - `esdata3`
     - `rabbitmqdata`
     - `redisdata`
     - `hyperiondata`

### How to Use

1. Ensure that you have necessary permissions to execute the script.
2. Run the script from the project's root directory: cleanup.sh
3. The script will automatically stop the Docker Compose services and remove the listed volumes.

### Important Notes

- **Data Loss Warning:** Running this script will permanently delete the listed Docker volumes. Make sure to backup any important data before running the script.
- **Prerequisites:** This script requires Docker and Docker Compose to be installed and assumes that you are running it from the project's root directory.
- **Commented Command:** The `docker system prune -a --volumes` command is commented out in the script. You can uncomment this line to remove all unused Docker images, containers, and volumes, but be cautious as this will affect resources beyond this project.

---

This section provides clear instructions and important notes about the `cleanup.sh` script, ensuring that users understand its purpose and the implications of running it. It's important to highlight the potential for data loss to prevent accidental deletion of important data.

## Testing Blockchain Syncing and Hyperion Indexing

We provide a script to facilitate the testing of blockchain syncing and Hyperion indexing. This script ensures the necessary services are started and executes specific tasks within the `node` and `hyperion` containers.

### Script Contents

The script performs the following actions:

1. **Start Node Service:**
   - Executes `docker exec -d node bash start.sh` to start the blockchain node service in the background.
2. **Delay Execution:**
   - Waits for 10 seconds (using `sleep 10`) to allow the node service to initialize properly.
3. **Start Hyperion Indexing:**
   - Executes `docker exec -d hyperion bash run.sh wax-indexer` to start the Hyperion indexing process for the blockchain data.

### How to Use

1. Make sure the Docker containers for `node` and `hyperion` are up and running.
2. Run the script from the project's root directory: /test-runs/testrun.sh
3. The script will initiate the processes in the respective containers in the background.

### Important Notes

- **Purpose of the Script:** This script is particularly useful for testing and ensuring that the blockchain syncing and Hyperion indexing services are functioning as expected.
- **Customization:** You may need to modify the script (e.g., the sleep duration or commands) based on your specific environment or testing requirements.
- **Prerequisites:** This script requires Docker to be installed and assumes that all related containers are correctly set up and configured.

---

This section in your `README.md` provides a clear understanding of what the script does, how to use it, and important considerations. It's structured to guide the user through the process, ensuring they are aware of the purpose and requirements of the script.

