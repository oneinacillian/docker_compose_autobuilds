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
| ES Exporters | Elasticsearch Metrics | 9114+ | Hyperion |

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

# Elasticsearch settings
ES_HEAP_DUMP_PATH=/var/log/elasticsearch
ES_GC_LOG_PATH=/var/log/elasticsearch
ES_JAVA_OPTS="-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=${ES_HEAP_DUMP_PATH}"

# Monitoring configuration
MONITORING_ENABLED=true
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

### Monitoring Toggle
You can enable or disable the monitoring stack (Prometheus, Grafana, and all exporters) by setting the `MONITORING_ENABLED` variable in your `.env` file:

```env
# Enable monitoring (default)
MONITORING_ENABLED=true

# Disable monitoring
MONITORING_ENABLED=false
```

When monitoring is disabled:
- Prometheus and Grafana containers will not be included in the compose file
- All exporters (Elasticsearch, Redis, RabbitMQ, Nodeos) will be excluded
- Prometheus configuration will not be updated
- Grafana data volume will not be created

This feature is useful for:
- Development environments where monitoring is not needed
- Resource-constrained systems
- Simplified deployments for testing
- Production environments where monitoring is handled separately

### Elasticsearch Configuration
The deployment automatically manages Elasticsearch configuration through `elasticsearch.yml` files. Each Elasticsearch node gets its own optimized configuration with the following settings:

```yaml
# Memory settings
indices.memory.index_buffer_size: 30%
indices.fielddata.cache.size: 25%
indices.queries.cache.size: 25%

# Thread pool settings
thread_pool:
  write:
    size: 8
    queue_size: 1000
  search:
    size: 12
    queue_size: 1000

# Recovery settings
indices.recovery.max_bytes_per_sec: 500mb
indices.recovery.max_concurrent_file_chunks: 8

# Cache and disk settings
cache.recycler.page.type: NONE
cluster.routing.allocation.disk.threshold_enabled: false
http.max_content_length: 500mb
```

These configurations are automatically generated and placed in:
```
elasticsearch/config/es{n}/elasticsearch.yml
```
Where `{n}` represents the node number (e.g., es1, es2, etc.)

#### Customizing Elasticsearch Configuration
To modify the default Elasticsearch settings:

1. Locate the `generate_elasticsearch_config()` function in `generate_hyperion_compose.py`:
```python
def generate_elasticsearch_config():
    return """
    # Memory settings
    indices.memory.index_buffer_size: 30%
    ...
    """
```

2. Edit the configuration string in this function to match your desired settings
3. Run the generation script again:
```bash
python3 generate_hyperion_compose.py
```

Common modifications include:
- Adjusting memory settings for different hardware configurations
- Modifying thread pool sizes for different workloads
- Changing recovery settings for network optimization
- Updating cache settings for memory management

> Note: Make sure to back up your configuration changes as they will be overwritten if you update the repository.

### Custom Elasticsearch Cluster
```bash
# Set desired node count in .env
AMOUNT_OF_NODE_INSTANCES=2
```

When you modify the `AMOUNT_OF_NODE_INSTANCES` in your `.env` file and run `generate_hyperion_compose.py`:
1. The script will generate the appropriate number of Elasticsearch nodes
2. It will create optimized elasticsearch.yml configurations for each node
3. It will automatically create corresponding Elasticsearch exporters (one per ES node)
4. The Prometheus configuration (`prometheus/hyperion/prometheus.yml`) will be dynamically updated to monitor all ES instances
5. Each ES exporter will be assigned a unique port starting from 9114 (e.g., 9114, 9115, etc.)

For example, with `AMOUNT_OF_NODE_INSTANCES=2`:
- ES Node 1 → elasticsearch-exporter-1:9114
- ES Node 2 → elasticsearch-exporter-2:9115

### PostgreSQL Optimizations
The PostgreSQL instance is automatically configured with performance optimizations based on the host system's resources:

- **shared_buffers**: Set to 25% of total system memory
- **work_mem**: Calculated based on max_connections and available memory
- **maintenance_work_mem**: Set to 5% of total system memory
- **effective_cache_size**: Set to 50% of total system memory
- **Extensions**: Automatically enables pg_trgm for improved text search capabilities

These optimizations are handled automatically during container initialization through the init-db.sh script.

## 📈 Recent Improvements

<details>
<summary><b>View Changelog</b></summary>

| Date | Improvement | Impact |
|------|------------|---------|
| 2025-01-05 | Added monitoring toggle feature | Resource Optimization |
| 2025-01-02 | Added automated Elasticsearch configuration management | Performance |
| 2025-01-01 | Added healthcheck to Elasticsearch | Monitoring |
| 2025-01-01 | Added ES heap dump and GC logging configuration | Debugging |
| 2024-12-24 | Added dynamic Prometheus configuration for ES exporters | Monitoring |
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
- `ES_HEAP_DUMP_PATH`: Directory path for Elasticsearch heap dumps (default: /var/log/elasticsearch)
- `ES_GC_LOG_PATH`: Directory path for Elasticsearch garbage collection logs (default: /var/log/elasticsearch)
- `ES_JAVA_OPTS`: Java options for Elasticsearch, including heap dump settings
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

### Monitoring Variables
- `MONITORING_ENABLED`: Enable or disable the monitoring stack (Prometheus, Grafana, and exporters)

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