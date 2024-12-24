# Docker Deployment Guide: Hyperion & Atomic Services

> Quick deployment solution for Hyperion and Atomic services with monitoring capabilities.

## 🚀 Quick Start

1. Clone and navigate to the project
2. Configure your `.env` file (see [Environment Setup](#-environment-setup))
3. Run the desired service:
```bash
# For Hyperion
docker-compose -f ./docker-compose-hyperion.yml up -d --build

# For Atomic
docker-compose -f ./docker-compose-atomic.yml up -d --build
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
ELASTICSEARCH_VERSION=8.11.4
KIBANA_VERSION=8.11.4
RABBITMQ_DEFAULT_USER=rabbitmquser
RABBITMQ_DEFAULT_PASS=rabbitmqpass
RABBITMQ_DEFAULT_VHOST=hyperion
HYPERION_ENVIRONMENT=testnet
HYPERION_LAUNCH_ON_STARTUP=false

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

# Generate compose file for hyperion
python3 generate_hyperion_compose.py

# Generate compose file for atomic
python3 generate_atomic_compose.py

# Launch hyperion with generated compose
docker compose -f docker-compose-generated-hyperion.yml up -d

# Launch atomic with generated compose
docker compose -f docker-compose-generated-atomic.yml up -d
```

### Cleanup
```bash
# Remove services with volumes
docker compose -f docker-compose-generated-atomic.yml down -v    # Atomic
docker compose -f docker-compose-generated-hyperion.yml down -v  # Hyperion
```

## 📈 Recent Improvements

<details>
<summary><b>View Changelog</b></summary>

| Date | Improvement | Impact |
|------|------------|---------|
| 2024-12-23 | Added Atomic monitoring (Postgres/Redis) | Monitoring |
| 2024-12-22 | Custom managed dashboards for nodeos | Monitoring |
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
- `ELASTICSEARCH_VERSION`: Elasticsearch version
- `KIBANA_VERSION`: Kibana version
- `HYPERION_VERSION`: Hyperion version
- `ELASTIC_MAX_MEM`/`ELASTIC_MIN_MEM`: ES memory limits
- [View all Hyperion variables...](#)

### Atomic Variables
- `SHIPHOST`/`SHIPPORT`: SHIP connection details
- `POSTGRES_*`: Database configuration
- [View all Atomic variables...](#)

</details>