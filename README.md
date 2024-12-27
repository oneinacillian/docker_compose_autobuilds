# Docker Deployment Guide: Hyperion & Atomic Services

> Quick deployment solution for Hyperion and Atomic services with monitoring capabilities.

## 🚀 Quick Start

1. Clone and navigate to the project
2. Configure your `.env` file (see [Environment Setup](#-environment-setup))
3. Run the Python script to generate the docker compose files:
```bash
# Generate Hyperion compose file            
python3 generate_hyperion_compose.py

# Generate Atomic compose file
python3 generate_atomic_compose.py
```
4. Run the desired service:
```bash
# For Hyperion
docker-compose -f ./docker-compose-generated-hyperion.yml up -d --build

# For Atomic
docker-compose -f ./docker-compose-generated-atomic.yml up -d --build
```
5. Stop the services:
```bash
# For Hyperion
docker-compose -f ./docker-compose-generated-hyperion.yml down

# For Atomic
docker-compose -f ./docker-compose-generated-atomic.yml down
``` 

## 📋 Services Overview

| Service | Purpose | Default Port | Stack |
|---------|---------|--------------|-------|
| Hyperion | History API & Indexer | 7000 | Hyperion |
| Elasticsearch | Search & Storage | 9200 | Hyperion |
| Kibana | Data Visualization | 5601 | Hyperion |
| RabbitMQ | Message Queue | 5672, 15672 | Hyperion |
| Redis | Caching Layer | 6379 | Both |
| Atomic API | NFT Data Provider | 28888 | Atomic |
| PostgreSQL | Database | 5432 | Atomic |
| Grafana | Metrics Dashboard | 3000 | Both |
| Prometheus | Metrics Collection | 9090 | Both |

## 📋 Prerequisites

- Docker & Docker Compose
- Elasticsearch configuration:
```bash
# Set vm.max_map_count
echo "vm.max_map_count=262144" >> /etc/sysctl.conf
sudo sysctl -p
```

## 🔧 Environment Setup

<details>
<summary><b>Sample .env Configuration</b></summary>

```env
# Hyperion Settings
ELASTICSEARCH_VERSION=8.13.2
KIBANA_VERSION=8.13.2
RABBITMQ_DEFAULT_USER=rabbitmquser
RABBITMQ_DEFAULT_PASS=rabbitmqpass
RABBITMQ_DEFAULT_VHOST=hyperion
HYPERION_ENVIRONMENT=testnet
HYPERION_LAUNCH_ON_STARTUP=false
HYPERION_VERSION=3.5.0
ELASTIC_MAX_MEM=15g
ELASTIC_MIN_MEM=15g
AMOUNT_OF_NODE_INSTANCES=2

# Atomic Settings
SHIPHOST=172.168.40.50
SHIPPORT=29876
HTTPHOST=172.168.40.50
HTTPPORT=28888
POSTGRES_USER=waxuser
POSTGRES_PASSWORD=waxuserpass
POSTGRES_DB=atomic
ATOMIC_ENVIRONMENT=testnet
ATOMIC_LAUNCH_ON_STARTUP=true

# Leap variables for Hyperion
LEAP_FILE=https://apt.eossweden.org/wax/pool/stable/w/wax-leap-503wax01/wax-leap-503wax01_5.0.3wax01-ubuntu-22.04_amd64.deb
LEAP_DEB_FILE=wax-leap-503wax01_5.0.3wax01-ubuntu-22.04_amd64.deb

# Grafana settings
GF_USERNAME=admin
GF_PASSWORD=admin123
```
</details>

## 🏗️ Architecture

### Hyperion Stack
- **Search & Analytics**: Elasticsearch cluster (configurable nodes)
- **Visualization**: Kibana
- **Caching**: Redis
- **Message Queue**: RabbitMQ
- **Monitoring**: Grafana + Prometheus
- **Custom Exporters**: Nodeos, RabbitMQ, Redis

### Atomic Stack
- **Database**: PostgreSQL (optimized configuration)
- **Caching**: Redis
- **Monitoring**: Grafana + Prometheus
- **Custom Exporters**: PostgreSQL, Redis

## 🛠️ Advanced Configuration

### Custom Elasticsearch Cluster
```bash
# Set desired node count in .env
AMOUNT_OF_NODE_INSTANCES=2
```

## 📈 Recent Improvements

<details>
<summary><b>View Changelog</b></summary>

| Date | Improvement | Impact |
|------|------------|---------|
| 2024-12-23 | Added Atomic monitoring (Postgres/Redis) + managed Grafana dashboards | Monitoring |
| 2024-12-23 | Added Hyperion monitoring (RabbitMQ/Redis) + managed Grafana dashboards | Monitoring |
| 2024-12-22 | Custom built exporters for nodeos + managed Grafana dashboards | Monitoring |
| 2024-11-20 | Scripted docker compose generation | Usability |
| 2024-07-14 | Customizable nodeos deployment | Flexibility |
| 2024-07-13 | Hyperion 3.3.10-1 verification | Stability |
| 2024-06-20 | Improved error handling and logging | Reliability |
| 2024-05-10 | Added automated backup solutions | Data Safety |
| 2024-04-15 | Enhanced security with localhost port binding | Security |

</details>

## 🔍 Troubleshooting

- Check container logs: `docker logs <container_name>`
- Ensure no port conflicts
- Verify environment variables are set correctly
- Confirm data volumes are properly mounted

## 📚 Documentation

<details>
<summary><b>Environment Variables Reference</b></summary>

### Hyperion Variables
- `ELASTICSEARCH_VERSION`: Specifies the version of Elasticsearch to be used in the services
- `KIBANA_VERSION`: Defines the version of Kibana for compatibility with Elasticsearch
- `HYPERION_VERSION`: Configure Hyperion Version deployment
- `ELASTIC_MAX_MEM`/`ELASTIC_MIN_MEM`: ES memory limits
- `RABBITMQ_DEFAULT_USER`: The default username for RabbitMQ access
- `RABBITMQ_DEFAULT_PASS`: The default password for RabbitMQ access
- `RABBITMQ_DEFAULT_VHOST`: The default virtual host in RabbitMQ, used for isolation and management of queues
- `HYPERION_ENVIRONMENT`: Hyperion environment
- `HYPERION_LAUNCH_ON_STARTUP`: Hyperion startup at launchtime (Ship + Hyperion indexer)
- `AMOUNT_OF_NODE_INSTANCES`: The amount of ES instances you would like to have part of your Elasticsearch solution

### Atomic Variables
-  `SHIPHOST`: WS connection to your full SHIP
-  `SHIPPORT`: WS port to your full SHIP
-  `HTTPHOST`: HTTP connection to your full SHIP
-  `HTTPPORT`: HTTP port to your full SHIP
-  `POSTGRES_USER`: User for Atomic DB
-  `POSTGRES_PASSWORD`: User password for Atomic DN
-  `POSTGRES_DB`: DB to be used for Atomic
-  `ATOMIC_LAUNCH_ON_STARTUP`: Atomic startup at launchtime

### Leap Variables for Hyperion
- `LEAP_FILE`: The full path of your nodeos deb file (i.e. https://apt.eossweden.org/wax/pool/stable/w/wax-leap-503wax01/wax-leap-503wax01_5.0.3wax01-ubuntu-22.04_amd64.deb)
- `LEAP_DEB_FILE`: deb filename to be used for the deployment above (i.e. wax-leap-503wax01_5.0.3wax01-ubuntu-22.04_amd64.deb)

### Grafana Variables
- `GF_USERNAME`: Grafana username
- `GF_PASSWORD`: Grafana password

</details>

<details>
<summary><b>Network Configuration</b></summary>

```env
# Mainnet setup
HYPERION_ENVIRONMENT=mainnet
ATOMIC_ENVIRONMENT=mainnet

# Testnet setup
HYPERION_ENVIRONMENT=testnet
ATOMIC_ENVIRONMENT=testnet
```
</details>

### Security Considerations

- Always change default passwords in production
- Use strong passwords for database and admin accounts
- Consider using environment-specific `.env` files
- Backup your `.env` file securely
- Don't commit `.env` files to version control