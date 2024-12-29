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
leap_file = os.getenv("LEAP_FILE","https://apt.eossweden.org/wax/pool/stable/w/wax-leap-404wax01/wax-leap-404wax01_4.0.4wax01-ubuntu-18.04_amd64.deb")
leap_deb_file=os.getenv("LEAP_DEB_FILE","wax-leap-404wax01_4.0.4wax01-ubuntu-18.04_amd64.deb")
gf_username=os.getenv("GF_USERNAME","admin")
gf_password=os.getenv("GF_PASSWORD","admin123")

# Before the base_compose definition, add this helper function
def generate_es_uri(node_count):
    uris = [f'http://es{i}:9200' for i in range(1, node_count + 1)]
    return ','.join(uris)

def generate_es_exporters(node_count):
    exporters = ""
    for i in range(1, node_count + 1):
        exporter = f"""
  elasticsearch-exporter-{i}:
    image: quay.io/prometheuscommunity/elasticsearch-exporter:latest
    container_name: elasticsearch-exporter-{i}
    command:
      - '--es.uri=http://es{i}:9200'
    ports:
      - "{9114 + i - 1}:9114"
    depends_on:
      - es{i}
    networks:
      - esnet
"""
        exporters += exporter
    return exporters

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

  redis-exporter:
    image: oliver006/redis_exporter:latest
    container_name: redis-exporter
    environment:
      - REDIS_ADDR=redis:6379
    ports:
      - "9121:9121"
    networks:
      - esnet
    depends_on:
      - redis      

  rabbitmq:
    build:
      context: ./rabbitmq/Deployment
      dockerfile: Dockerfile.rabbitmq  
    container_name: rabbitmq
    environment:
      - RABBITMQ_DEFAULT_USER={rabbitmq_user}
      - RABBITMQ_DEFAULT_PASS={rabbitmq_pass}
      - RABBITMQ_DEFAULT_VHOST={rabbitmq_vhost}
    command:
      - sh
      - -c
      - |
        rabbitmq-plugins disable --all &&
        rabbitmq-plugins enable rabbitmq_management rabbitmq_prometheus &&
        rabbitmq-server  
    ports:
      - "127.0.0.1:5672:5672"
      - "127.0.0.1:15672:15672"
      - "127.0.0.1:15692:15692"
    networks:
      - esnet
    volumes:
      - rabbitmqdata:/var/lib/rabbitmq
      - ./rabbitmq/Deployment/rabbitmq.conf:/etc/rabbitmq/rabbitmq.conf
      - ./rabbitmq/Deployment/rabbitmq-env.conf:/etc/rabbitmq/rabbitmq-env.conf   
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
      - "7000:7000"
      - "1234:1234"
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
        - LEAP_FILE={leap_file}
        - LEAP_DEB_FILE={leap_deb_file}
    ports:
      - "127.0.0.1:9876:9876"
      - "127.0.0.1:8888:8888"
    networks:
      - esnet
    volumes:
      - node:/app/node/data

  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/hyperion/prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
    networks:
      - esnet

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3030:3000"
    environment:
      - GF_SECURITY_ADMIN_USER={gf_username}
      - GF_SECURITY_ADMIN_PASSWORD={gf_password}
    volumes:
      - ./grafana/provisioning/hyperion:/etc/grafana/provisioning
      - grafana-data:/var/lib/grafana
    networks:
      - esnet

  nodeos-custom-exporter:
    build:
      context: ./custom-nodeos-exporter
      dockerfile: Dockerfile
    container_name: nodeos-custom-exporter
    ports:
      - "8000:8000"
    depends_on:
      - node
    networks:
      - esnet
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
  grafana-data:
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

# Combine everything - update this section at the end of the file
# Remove the elasticsearch exporters from base_compose if it exists
base_compose = base_compose.replace("""  elasticsearch-exporter:
    build:
      context: ./elasticsearch_exporter
      dockerfile: Dockerfile
    container_name: elasticsearch-exporter
    command:
      - "--es.uri={generate_es_uri(amount_of_nodes)}"
    ports:
      - "9114:9114"
    depends_on:
      - es1
    networks:
      - esnet""", "")

# Generate all services first, then volumes and networks
all_services = base_compose + services + generate_es_exporters(amount_of_nodes)

# Combine services with volumes and networks
final_compose = all_services + volumes_and_networks.format(volumes=volumes)

# Write to docker-compose.yml
with open("docker-compose-generated-hyperion.yml", "w") as f:
    f.write(final_compose)

print(f"Generated docker-compose-generated-hyperion.yml with {amount_of_nodes} Elasticsearch nodes.")

def update_prometheus_config(node_count):
    # Read the existing prometheus.yml
    with open("prometheus/hyperion/prometheus.yml", "r") as f:
        config = f.read()

    # Find and replace the elasticsearch_exporter job
    old_es_job = """  - job_name: elasticsearch_exporter
    scrape_interval: 1s
    static_configs:
      - targets: ["elasticsearch-exporter-1:9114"]"""

    # Generate new targets list based on node count
    targets = '", "'.join([f'elasticsearch-exporter-{i}:9114' for i in range(1, node_count + 1)])
    new_es_job = f"""  - job_name: elasticsearch_exporter
    scrape_interval: 1s
    static_configs:
      - targets: ["{targets}"]"""

    # Replace the old job configuration with the new one
    updated_config = config.replace(old_es_job, new_es_job)

    # Write the updated configuration back to the file
    with open("prometheus/hyperion/prometheus.yml", "w") as f:
        f.write(updated_config)

# Add this line at the end of the script, after writing the docker-compose file
update_prometheus_config(amount_of_nodes)
print(f"Updated prometheus.yml with {amount_of_nodes} elasticsearch-exporter targets.")
