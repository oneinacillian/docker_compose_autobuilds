import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load the number of nodes and other configurations from the environment
amount_of_nodes = int(os.getenv("AMOUNT_OF_NODE_INSTANCES", 1))
elasticsearch_version = os.getenv("ELASTICSEARCH_VERSION", "8.13.2")
elastic_min_mem = os.getenv("ELASTIC_MIN_MEM", "1g")
elastic_max_mem = os.getenv("ELASTIC_MAX_MEM", "2g")
kibana_version = os.getenv("KIBANA_VERSION", "8.13.2")
rabbitmq_user = os.getenv("RABBITMQ_DEFAULT_USER", "rabbitmquser")
rabbitmq_pass = os.getenv("RABBITMQ_DEFAULT_PASS", "rabbitmqpass")
rabbitmq_vhost = os.getenv("RABBITMQ_DEFAULT_VHOST", "hyperion")
hyperion_environment = os.getenv("HYPERION_ENVIRONMENT", "testnet")
hyperion_launch_on_startup = os.getenv("HYPERION_LAUNCH_ON_STARTUP", "false")
hyperion_version = os.getenv("HYPERION_VERSION", "v3.3.10-1")

# Base fixed Docker Compose services
base_compose = f"""
version: '3'
services:
  kibana:
    image: docker.elastic.co/kibana/kibana:{kibana_version}
    container_name: kibana
    environment:
      - "ELASTICSEARCH_URL=http://es1:9200"
      - "ELASTICSEARCH_HOSTS=http://es1:9200"
    ports:
      - "5601:5601"
    depends_on:
      - es1
    networks:
      - esnet
    healthcheck:
      test: ["CMD-SHELL", "curl --silent --fail http://localhost:5601/api/status || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5

  redis:
    image: "redis:latest"
    container_name: redis
    ports:
      - "127.0.0.1:6379:6379"
    networks:
      - esnet
    volumes:
      - redisdata:/data
    command: redis-server --appendonly yes --supervised systemd --maxmemory 10gb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  rabbitmq:
    image: "rabbitmq:3-management"
    container_name: rabbitmq
    environment:
      - RABBITMQ_DEFAULT_USER={rabbitmq_user}
      - RABBITMQ_DEFAULT_PASS={rabbitmq_pass}
      - RABBITMQ_DEFAULT_VHOST={rabbitmq_vhost}
    ports:
      - "127.0.0.1:5672:5672"
      - "127.0.0.1:15672:15672"
    networks:
      - esnet
    volumes:
      - rabbitmqdata:/var/lib/rabbitmq
    healthcheck:
      test: ["CMD", "rabbitmqctl", "status"]
      interval: 30s
      timeout: 10s
      retries: 5

  hyperion:
    container_name: hyperion
    tty: true
    build:
      context: ./hyperion/Deployment
      dockerfile: Dockerfile.hyperion
      args:
        - HYPERION_ENVIRONMENT={hyperion_environment}
        - HYPERION_LAUNCH_ON_STARTUP={hyperion_launch_on_startup}
        - HYPERION_VERSION={hyperion_version}
        - RABBITMQ_DEFAULT_USER={rabbitmq_user}
        - RABBITMQ_DEFAULT_PASS={rabbitmq_pass}
    ports:
      - "127.0.0.1:7000:7000"
      - "127.0.0.1:1234:1234"
    networks:
      - esnet
    volumes:
      - hyperiondata:/app/hyperiondata
    depends_on:
      - redis
      - rabbitmq
      - es1

  node:
    container_name: node
    tty: true
    build:
      context: ./hyperion/Deployment
      dockerfile: Dockerfile.node
      args:
        - HYPERION_ENVIRONMENT={hyperion_environment}
        - HYPERION_LAUNCH_ON_STARTUP={hyperion_launch_on_startup}
    ports:
      - "127.0.0.1:9876:9876"
      - "127.0.0.1:8888:8888"
    networks:
      - esnet
    volumes:
      - node:/app/node/data
"""

# Template for Elasticsearch nodes
node_template = """
  es{index}:
    image: docker.elastic.co/elasticsearch/elasticsearch:{version}
    container_name: es{index}
    environment:
      - "node.name=es{index}"
      - "cluster.name=es-docker-cluster"
      - "cluster.initial_master_nodes={initial_master_nodes}"
      - "discovery.seed_hosts={seed_hosts}"
      - "ES_JAVA_OPTS=-Xms{min_mem} -Xmx{max_mem}"
      - "xpack.security.enabled=false"
      - "xpack.monitoring.collection.enabled=true"
      - "bootstrap.memory_lock=false"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - esdata{index}:/usr/share/elasticsearch/data
    networks:
      - esnet
"""

# Base for volumes and networks
volumes_and_networks = """
volumes:
  redisdata:
  rabbitmqdata:
  hyperiondata:
  node:
{volumes}

networks:
  esnet:
"""

# Generate Elasticsearch services
services = ""
initial_master_nodes = ",".join([f"es{i}" for i in range(1, amount_of_nodes + 1)])
seed_hosts = initial_master_nodes

for i in range(1, amount_of_nodes + 1):
    services += node_template.format(
        index=i,
        version=elasticsearch_version,
        initial_master_nodes=initial_master_nodes,
        seed_hosts=seed_hosts,
        min_mem=elastic_min_mem,
        max_mem=elastic_max_mem
    )

# Generate volumes for Elasticsearch
volumes = "\n".join([f"  esdata{i}:" for i in range(1, amount_of_nodes + 1)])

# Combine everything
final_compose = base_compose + services + volumes_and_networks.format(volumes=volumes)

# Write to docker-compose.yml
with open("docker-compose-generated.yml", "w") as f:
    f.write(final_compose)

print(f"Generated docker-compose.yml with {amount_of_nodes} Elasticsearch nodes.")
