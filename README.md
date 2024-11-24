# Project Deployment Documentation

## Introduction
This document provides detailed information about the deployment of our Dockerized services using Docker Compose. It includes configuration details and instructions for setting up and running Hyperion and Atomic services.

## Prerequisites
- Docker and Docker Compose installed on your machine.
- Basic understanding of Docker and containerization.
- Necessary environment variables set in your .env file <br>
   ```
   ELASTICSEARCH_VERSION=8.11.4
   KIBANA_VERSION=8.11.4
   RABBITMQ_DEFAULT_USER=rabbitmquser
   RABBITMQ_DEFAULT_PASS=rabbitmqpass
   RABBITMQ_DEFAULT_VHOST=hyperion
   HYPERION_ENVIRONMENT=testnet
   HYPERION_LAUNCH_ON_STARTUP=false

   SHIPHOST=172.168.40.50
   SHIPPORT=29876
   HTTPHOST=172.168.40.50
   HTTPPORT=28888
   POSTGRES_USER=waxuser
   POSTGRES_PASSWORD=waxuserpass
   POSTGRES_DB=atomic
   ATOMIC_ENVIRONMENT=testnet
   ATOMIC_LAUNCH_ON_STARTUP=true
   ```

- Ensure that you configure vm.max_map_count to at least 262144 for optimal Elasticsearch operation

   ```
   edit /etc/sysctl.conf
   add => vm.max_map_count=262144
   run => sudo sysctl -p
   ```

## Services Overview (Hyperion)
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

## Services Overview (Atomic)
1. **Redis:**
   - In-memory data store, used as a database, cache, and message broker.
   - Append-only data persistence and LRU eviction policy.
   - Health check for ensuring service responsiveness.
2. **Postgres:**
   - PostgreSQL is an advanced, open-source relational database management system (RDBMS) that supports both SQL (Structured Query Language) for relational queries and JSON (JavaScript Object Notation) for non-relational queries
   - Initialization:
      ```
      Allow connections on all network interfaces (listen_addresses = '*').
      Adjust shared_buffers to 25% of total memory.
      Configure work_mem based on total memory and max_connections, aiming for a portion of total memory divided by the number of connections, adjusted for 256kB segments.
      Set maintenance_work_mem to 5% of total memory.
      Define effective_cache_size as 50% of total memory.
      Executes a PostgreSQL command to create the pg_trgm extension if it does not exist.
      ```
   - Persistent volume for data and configurations.
3. **Atomic (Custom Service):**
   - Custom service built with specific Dockerfile and environment settings.
   - Dependent on Elasticsearch (postgres, redis).
   - Port and volume configurations as per application requirements.

## Getting Started
1. Clone the repository and navigate to the project directory.
2. Ensure all environment variables are correctly set in your .env file.
3. To run Hyperion or Atomic, run command: 
   ```
   docker-compose -f ./docker-compose-hyperion.yml up -d --build
   docker-compose -f ./docker-compose-atomic.yml up -d --build
   ```
   The service will run in detached mode
4. Check the status of all services using `docker-compose ps`.
5. To bring down the environment, run:
   ```
   docker-compose -f ./docker-compose-atomic.yml down -v to bring down Atomic (-v flag to prune service completely, with the data volumes)
   docker-compose -f ./docker-compose-hyperion.yml down -v to bring down Hyperion (-v flag to prune service completely, with the data volumes)
   ```
6. If you would like to generate your compose for hyperion by specifying a custom ES node configuration, select your amount of ES instances in the .env:
   ```
   AMOUNT_OF_NODE_INSTANCES=2
   ```
   Then run the following to generate the compose
   ```
   python3 generate_compose.py
   ```
   The start the solution using the generated compose (the compose filename being generated will be docker-compose-generated.yml )
   ```
   docker compose -f docker-compose-generated.yml up -d
   ```


## Additional Information
- **Configuration Adjustments:** Make any necessary changes to the `.yml` and `.json` files to suit your environment.
- **Port Conflicts:** Ensure no conflicts with existing services running on the same ports.
- **Data Persistence:** Data volumes are set up for persistence. Adjust volume bindings as necessary.

## Troubleshooting
- If a service fails to start, check the Docker logs for that container for more information

### Explanation of Variables (.env)

> Hyperion

- `ELASTICSEARCH_VERSION`: Specifies the version of Elasticsearch to be used in the services.
- `KIBANA_VERSION`: Defines the version of Kibana for compatibility with Elasticsearch.
- `RABBITMQ_DEFAULT_USER`: The default username for RabbitMQ access.
- `RABBITMQ_DEFAULT_PASS`: The password for the RabbitMQ user.
- `RABBITMQ_DEFAULT_VHOST`: The default virtual host in RabbitMQ, used for isolation and management of queues.
- `HYPERION_ENVIRONMENT`: Indicates the environment setting, which can be adjusted based on the deployment stage (e.g., testnet, mainnet).
- `HYPERION_LAUNCH_ON_STARTUP`: Hyperion startup at launchtime (Ship + Hyperion indexer)
- `ELASTIC_MAX_MEM`: Configure Elastic Max Memory parameter for es nodes
- `ELASTIC_MIN_MEM`: Configure Elastic Min Memory parameter for es nodes
- `HYPERION_VERSION`: Configure Hyperion Version deployment
- `LEAP_FILE`: The full path of your nodeos deb file (i.e. https://apt.eossweden.org/wax/pool/stable/w/wax-leap-404wax01/wax-leap-404wax01_4.0.4wax01-ubuntu-18.04_amd64.deb)
- `LEAP_DEB_FILE`: deb filename to be used for the deployment above (i.e. wax-leap-404wax01_4.0.4wax01-ubuntu-18.04_amd64.deb)
- `AMOUNT_OF_NODE_INSTANCES`: The amount of ES instances you would like to have part of your Elasticsearch solution

> Atomic

-  `SHIPHOST`: WS connection to your full SHIP
-  `SHIPPORT`: WS connection to your full SHIP
-  `HTTPHOST`: HTTP connection to your full SHIP
-  `HTTPPORT`: HTTP connection to your full SHIP
-  `POSTGRES_USER`: User for Atomic DB
-  `POSTGRES_PASSWORD`: User password for Atomic DN
-  `POSTGRES_DB`: DB to be used for Atomic
-  `ATOMIC_ENVIRONMENT`: Indicates the environment setting, which can be adjusted based on the deployment stage (e.g., testnet, mainnet).
-  `ATOMIC_LAUNCH_ON_STARTUP`: Atomic startup at launchtime

### Setting up the .env File

1. Copy the above content into a new file named `.env` in the same directory as your `docker-compose.yml`.
2. Adjust the values as needed to fit your specific environment or version requirements.
3. Ensure that the `.env` file is not committed to version control if it contains sensitive information (add `.env` to your `.gitignore` file).

By configuring these environment variables, the Docker Compose services will automatically use them during the deployment process. This setup ensures easy management and configuration of your services.

### Important Notes

- **Data Loss Warning:** Running this script will permanently delete the listed Docker volumes. Make sure to backup any important data before running the script.
- **Prerequisites:** This script requires Docker and Docker Compose to be installed and assumes that you are running it from the project's root directory.

<br>
<br>


| Improvement Made | Area of Impact | Date Implemented | Notes |
|------------------|----------------|------------------|-------|
| Use vendor images | Performance/Stability | 2024-02-11 | Applications built on optimized images |
| Add Atomic deployment | Usability | 2024-02-11 | Quick/Customizable Atomic deployments for use/testing |
| Customize environment | Usability | 2024-02-11 | Option to auto-launch applications for quick testing |
| Incorporate dependency checks on services | Usability | 2023-02-13 | Ensure dependent services up before running hyperion / Atomic
| Latest version of Elastic verified | Stability | 2024-04-15 | Successfully tested on Hyperion 3.3.9-8
| Lock down ports on docker to localhost on Hyperion| Security | 2024-04-15 | In case docker networking and firewalling is not understood
| Externalize Hyperion version | Usability | 2024-07-13 | Easily set/upgrade Hyperion versions
| Externalize Memory parameters for ES | Usability | 2024-07-13 | Easily manage ES memory parameters
| Latest version of Hyperion (3.3.10-1) verified | Stability | 2024-07-13 | Confirm index operation and health status on API
| Customize nodeos deployment | Usability | 2024-07-14 | You can now control your nodeos deployment from your .env + smaller git footprint
| Enable scripted docker compose | Usability | 2024-11-20 | You can now specify your amount of ES nodes, and your compose will be generated
| Improve Rabbitmq deployment | Compatibility | 2024-11-20 | Custom config. Hyperion compatibility