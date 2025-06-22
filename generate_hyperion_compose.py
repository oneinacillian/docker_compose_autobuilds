import os
from dotenv import load_dotenv

def generate_elasticsearch_config():
    return """
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

# Cache settings
cache.recycler.page.type: NONE

# Disk settings
cluster.routing.allocation.disk.threshold_enabled: false

# HTTP settings
http.max_content_length: 500mb
"""

def setup_elasticsearch_config(node_count):
    import os
    
    # Create base elasticsearch config directory
    os.makedirs("elasticsearch/config", exist_ok=True)
    
    # Generate elasticsearch.yml content
    es_config = generate_elasticsearch_config()
    
    # Create config directory and files for each node
    for i in range(1, node_count + 1):
        node_config_dir = f"elasticsearch/config/es{i}"
        os.makedirs(node_config_dir, exist_ok=True)
        
        # Write elasticsearch.yml only
        with open(f"{node_config_dir}/elasticsearch.yml", "w") as f:
            f.write(es_config)

def setup_rabbitmq_cluster_config(instance_count):
    """Setup RabbitMQ cluster configuration files"""
    if instance_count == 1:
        print("Single RabbitMQ instance, using standard configuration.")
        return
    
    # Create cluster configuration
    cluster_config = """# rabbitmq-cluster.conf
# Memory and resource management
vm_memory_high_watermark.relative = 0.4
vm_memory_high_watermark_paging_ratio = 0.5
disk_free_limit.relative = 1.0

# Cluster settings
cluster_formation.peer_discovery_backend = rabbit_peer_discovery_classic_config
"""
    
    # Add cluster nodes configuration
    for i in range(1, instance_count + 1):
        cluster_config += f"cluster_formation.classic_config.nodes.{i} = rabbit@rabbitmq-{i}\n"
    
    cluster_config += """
# Queue performance tuning for cluster
queue_index_embed_msgs_below = 4096
num_acceptors.tcp = 8
num_acceptors.ssl = 0

# Message handling
channel_max = 2000
max_message_size = 134217728

# Persistence and sync for cluster
queue_master_locator = client-local
mirroring_sync_batch_size = 4096

# Cluster-specific settings
cluster_partition_handling = autoheal
cluster_keepalive_interval = 10000

# Resource allocation
reverse_dns_lookups = false

# Management plugin settings
management.rates_mode = none

# Sample retention policies for management plugin
management.sample_retention_policies.global.minute = 5
management.sample_retention_policies.global.hour = 60
management.sample_retention_policies.global.day = 1200
management.sample_retention_policies.basic.minute = 5
management.sample_retention_policies.basic.hour = 60
management.sample_retention_policies.detailed.10 = 5

# Logging
log.file.level = warning

# TCP tuning for cluster
tcp_listen_options.backlog = 256
tcp_listen_options.nodelay = true
tcp_listen_options.keepalive = true

# Network partition handling
net_ticktime = 60
heartbeat = 60

# Performance tuning for high-throughput
vm_memory_high_watermark_paging_ratio = 0.5
queue_master_locator = min-masters

# Connection limits for cluster
connection_max = 10000
"""
    
    # Write cluster configuration
    with open("rabbitmq/Deployment/rabbitmq-cluster.conf", "w") as f:
        f.write(cluster_config)
    
    # Create dynamic nginx configuration for load balancer
    nginx_config = """events {
    worker_connections 1024;
}

http {
    upstream rabbitmq_management {
        # Load balance across all RabbitMQ nodes
"""
    
    for i in range(1, instance_count + 1):
        nginx_config += f"        server rabbitmq-{i}:15672;\n"
    
    nginx_config += """    }

    upstream rabbitmq_amqp {
        # Load balance AMQP connections
"""
    
    for i in range(1, instance_count + 1):
        nginx_config += f"        server rabbitmq-{i}:5672;\n"
    
    nginx_config += """    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=rabbitmq:10m rate=10r/s;

    server {
        listen 80;
        server_name localhost;

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\\n";
            add_header Content-Type text/plain;
        }

        # RabbitMQ Management UI
        location / {
            limit_req zone=rabbitmq burst=20 nodelay;
            
            proxy_pass http://rabbitmq_management;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support for management UI
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            
            # Timeouts
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        # RabbitMQ Prometheus metrics
        location /metrics {
            proxy_pass http://rabbitmq_management/metrics;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
"""
    
    # Write nginx configuration
    with open("rabbitmq/Deployment/nginx.conf", "w") as f:
        f.write(nginx_config)
    
    print(f"Created RabbitMQ cluster configuration for {instance_count} instances.")

def setup_rabbitmq_haproxy_config(instance_count, user, password):
    """Generate HAProxy configuration for RabbitMQ cluster"""
    import os
    
    # Create rabbitmq/Deployment directory if it doesn't exist
    os.makedirs("rabbitmq/Deployment", exist_ok=True)
    
    # Generate server entries for all RabbitMQ instances
    server_entries = ""
    for i in range(1, instance_count + 1):
        server_entries += f"    server rabbitmq-{i} rabbitmq-{i}:5672 check inter 2s rise 2 fall 3\n"
    
    # Generate HTTP server entries for management API
    http_server_entries = ""
    for i in range(1, instance_count + 1):
        http_server_entries += f"    server rabbitmq-{i} rabbitmq-{i}:15672 check inter 2s rise 2 fall 3\n"
    
    # Generate Prometheus server entries
    prometheus_server_entries = ""
    for i in range(1, instance_count + 1):
        prometheus_server_entries += f"    server rabbitmq-{i} rabbitmq-{i}:15692 check inter 2s rise 2 fall 3\n"
    
    # Create base64 encoded credentials for HTTP health check
    import base64
    credentials = f"{user}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    # Generate HAProxy configuration
    haproxy_cfg = f"""global
    log /dev/log local0
    maxconn 4096
    user haproxy
    group haproxy
    daemon

defaults
    log     global
    mode    tcp
    option  tcplog
    option  dontlognull
    timeout connect 5000
    timeout client  50000
    timeout server  50000

# AMQP Load Balancer for Hyperion
frontend amqp_frontend
    bind *:5672
    mode tcp
    default_backend amqp_backend

backend amqp_backend
    mode tcp
    balance roundrobin
    option tcp-check
    tcp-check connect port 5672
{server_entries}
# HTTP Management Load Balancer
frontend http_frontend
    bind *:15672
    mode http
    default_backend http_backend

backend http_backend
    mode http
    balance roundrobin
    option httpchk GET /api/overview
    http-check send meth GET uri /api/overview ver HTTP/1.1 hdr Host rabbitmq-loadbalancer hdr Authorization "Basic {encoded_credentials}" hdr Connection close
    http-check expect status 200
{http_server_entries}
# Prometheus Metrics Load Balancer
frontend prometheus_frontend
    bind *:15692
    mode http
    default_backend prometheus_backend

backend prometheus_backend
    mode http
    balance roundrobin
    option httpchk GET /metrics
    http-check expect status 200
{prometheus_server_entries}"""
    
    # Write the haproxy.cfg file
    with open("rabbitmq/Deployment/haproxy.cfg", "w") as f:
        f.write(haproxy_cfg)
    
    print(f"Generated RabbitMQ HAProxy configuration for {instance_count} instances")

# Load environment variables from .env file
load_dotenv()

# Add these new environment variables
es_heap_dump_path = os.getenv("ES_HEAP_DUMP_PATH", "/var/log/elasticsearch")
es_gc_log_path = os.getenv("ES_GC_LOG_PATH", "/var/log/elasticsearch")
es_java_opts = os.getenv("ES_JAVA_OPTS", "-XX:+HeapDumpOnOutOfMemoryError")
monitoring_enabled = os.getenv("MONITORING_ENABLED", "true").lower() == "true"
proxy_enabled = os.getenv("PROXY_ENABLED", "false").lower() == "true"
haproxy_http_port = os.getenv("HAPROXY_HTTP_PORT", "80")
haproxy_https_port = os.getenv("HAPROXY_HTTPS_PORT", "443")
haproxy_memory = os.getenv("HAPROXY_MEMORY", "1g")
haproxy_cpus = os.getenv("HAPROXY_CPUS", "1")
certbot_enabled = os.getenv("CERTBOT_ENABLED", "false").lower() == "true"
certbot_email = os.getenv("CERTBOT_EMAIL", "")
certbot_staging = os.getenv("CERTBOT_STAGING", "true").lower() == "true"

# Certificate request flags
request_kibana_cert = os.getenv("REQUEST_KIBANA_CERT", "true").lower() == "true"
request_grafana_cert = os.getenv("REQUEST_GRAFANA_CERT", "true").lower() == "true"
request_hyperion_cert = os.getenv("REQUEST_HYPERION_CERT", "true").lower() == "true"

# Load the number of nodes and other configurations from the environment
amount_of_nodes = int(os.getenv("AMOUNT_OF_NODE_INSTANCES", 1))
# Add RabbitMQ clustering configuration
amount_of_rabbitmq_instances = int(os.getenv("AMOUNT_OF_RABBITMQ_INSTANCES", 1))
rabbitmq_cluster_name = os.getenv("RABBITMQ_CLUSTER_NAME", "hyperion-cluster")
rabbitmq_erlang_cookie = os.getenv("RABBITMQ_ERLANG_COOKIE", "SWQOKODSQALRPCLNMEQG")
elasticsearch_version = os.getenv("ELASTICSEARCH_VERSION", "8.17.0")
elastic_min_mem = os.getenv("ELASTIC_MIN_MEM", "15g")
elastic_max_mem = os.getenv("ELASTIC_MAX_MEM", "15g")
kibana_version = os.getenv("KIBANA_VERSION", "8.17.0")
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

# Resource constraints
redis_memory = os.getenv("REDIS_MEMORY", "2g")
redis_cpus = os.getenv("REDIS_CPUS", "1")
rabbitmq_memory = os.getenv("RABBITMQ_MEMORY", "2g")
rabbitmq_cpus = os.getenv("RABBITMQ_CPUS", "1")
hyperion_memory = os.getenv("HYPERION_MEMORY", "8g")
hyperion_cpus = os.getenv("HYPERION_CPUS", "2")
node_memory = os.getenv("NODE_MEMORY", "16g")
node_cpus = os.getenv("NODE_CPUS", "4")
kibana_memory = os.getenv("KIBANA_MEMORY", "2g")
kibana_cpus = os.getenv("KIBANA_CPUS", "1")
prometheus_memory = os.getenv("PROMETHEUS_MEMORY", "2g")
prometheus_cpus = os.getenv("PROMETHEUS_CPUS", "1")
grafana_memory = os.getenv("GRAFANA_MEMORY", "1g")
grafana_cpus = os.getenv("GRAFANA_CPUS", "1")

# Replace the existing production_alias variable with these
production_alias_kibana = os.getenv("PRODUCTION_ALIAS_KIBANA", "")
production_alias_grafana = os.getenv("PRODUCTION_ALIAS_GRAFANA", "")
production_alias_hyperion = os.getenv("PRODUCTION_ALIAS_HYPERION", "")

# Before the base_compose definition, add this helper function
def generate_es_uri(node_count):
    uris = [f'http://es{i}:9200' for i in range(1, node_count + 1)]
    return ','.join(uris)

def generate_es_exporters(node_count):
    if not monitoring_enabled:
        return ""
        
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

def generate_rabbitmq_cluster_services(instance_count, cluster_name, erlang_cookie, user, password, vhost, memory, cpus):
    """Generate RabbitMQ cluster services configuration"""
    if instance_count == 1:
        # Single instance - no clustering needed
        return f"""
  rabbitmq:
    build:
      context: ./rabbitmq/Deployment
      dockerfile: Dockerfile.rabbitmq  
    container_name: rabbitmq
    environment:
      - RABBITMQ_DEFAULT_USER={user}
      - RABBITMQ_DEFAULT_PASS={password}
      - RABBITMQ_DEFAULT_VHOST={vhost}
      - RABBITMQ_ERLANG_COOKIE={erlang_cookie}
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
    deploy:
      resources:
        limits:
          memory: {memory}
          cpus: "{cpus}"
    volumes:
      - rabbitmqdata:/var/lib/rabbitmq
      - ./rabbitmq/Deployment/rabbitmq.conf:/etc/rabbitmq/rabbitmq.conf
      - ./rabbitmq/Deployment/rabbitmq-env.conf:/etc/rabbitmq/rabbitmq-env.conf   
    healthcheck:
      test: ["CMD", "rabbitmqctl", "status"]
      interval: 30s
      timeout: 10s
      retries: 5
"""
    
    # Multi-instance cluster
    cluster_services = ""
    for i in range(1, instance_count + 1):
        node_name = f"rabbitmq-{i}"
        is_first_node = i == 1
        
        # Generate cluster join command for non-first nodes
        cluster_join_cmd = ""
        if not is_first_node:
            cluster_join_cmd = f"""
        # Join cluster with first node
        sleep 30 &&
        rabbitmqctl stop_app &&
        rabbitmqctl reset &&
        rabbitmqctl join_cluster rabbit@rabbitmq-1 &&
        rabbitmqctl start_app &&"""
        
        service = f"""
  {node_name}:
    build:
      context: ./rabbitmq/Deployment
      dockerfile: Dockerfile.rabbitmq  
    container_name: {node_name}
    hostname: {node_name}
    environment:
      - RABBITMQ_DEFAULT_USER={user}
      - RABBITMQ_DEFAULT_PASS={password}
      - RABBITMQ_DEFAULT_VHOST={vhost}
      - RABBITMQ_ERLANG_COOKIE={erlang_cookie}
      - RABBITMQ_NODENAME=rabbit@{node_name}
      - RABBITMQ_USE_LONGNAME=false
    command:
      - sh
      - -c
      - |
        rabbitmq-plugins disable --all &&
        rabbitmq-plugins enable rabbitmq_management rabbitmq_prometheus &&
        rabbitmq-server &
        sleep 10 &&{cluster_join_cmd}
        wait
    ports:
      - "127.0.0.1:{5671 + i}:5672"
      - "127.0.0.1:{15671 + i}:15672"
      - "127.0.0.1:{15691 + i}:15692"
    networks:
      - esnet
    deploy:
      resources:
        limits:
          memory: {memory}
          cpus: "{cpus}"
    volumes:
      - rabbitmqdata{i}:/var/lib/rabbitmq
      - ./rabbitmq/Deployment/rabbitmq-cluster.conf:/etc/rabbitmq/rabbitmq.conf
      - ./rabbitmq/Deployment/rabbitmq-env.conf:/etc/rabbitmq/rabbitmq-env.conf   
    healthcheck:
      test: ["CMD", "rabbitmqctl", "status"]
      interval: 30s
      timeout: 10s
      retries: 5"""
        
        # Only add depends_on for non-first nodes
        if not is_first_node:
            service += f"""
    depends_on:
      - rabbitmq-1"""
        
        service += "\n"
        cluster_services += service
    
    # Add RabbitMQ load balancer for management interface
    # Generate depends_on list for all RabbitMQ instances
    depends_on_list = ""
    for i in range(1, instance_count + 1):
        depends_on_list += f"      - rabbitmq-{i}\n"
    
    cluster_services += f"""
  rabbitmq-loadbalancer:
    image: haproxy:2.8-alpine
    container_name: rabbitmq-loadbalancer
    ports:
      - "0.0.0.0:5675:5672"
      - "0.0.0.0:15675:15672"
      - "0.0.0.0:15695:15692"
    volumes:
      - ./rabbitmq/Deployment/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro
    networks:
      - esnet
    depends_on:
{depends_on_list.rstrip()}
    healthcheck:
      test: ["CMD", "haproxy", "-c", "-f", "/usr/local/etc/haproxy/haproxy.cfg"]
      interval: 30s
      timeout: 10s
      retries: 3
"""
    
    return cluster_services

def generate_rabbitmq_volumes(instance_count):
    """Generate RabbitMQ volumes for cluster"""
    if instance_count == 1:
        return "  rabbitmqdata:"
    
    volumes = ""
    for i in range(1, instance_count + 1):
        volumes += f"\n  rabbitmqdata{i}:"
    return volumes

# Define monitoring services separately
monitoring_services = f"""
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
    deploy:
      resources:
        limits:
          memory: {prometheus_memory}
          cpus: "{prometheus_cpus}"

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
    deploy:
      resources:
        limits:
          memory: {grafana_memory}
          cpus: "{grafana_cpus}"

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
"""

def generate_rabbitmq_exporters(instance_count):
    """Generate RabbitMQ exporters for cluster monitoring"""
    if not monitoring_enabled:
        return ""
    
    if instance_count == 1:
        return """
  rabbitmq-exporter:
    image: kbudde/rabbitmq-exporter:latest
    container_name: rabbitmq-exporter
    environment:
      - RABBIT_URL=http://rabbitmq:15672
      - RABBIT_USER=rabbitmquser
      - RABBIT_PASSWORD=rabbitmqpass
    ports:
      - "9419:9419"
    networks:
      - esnet
    depends_on:
      - rabbitmq
"""
    
    exporters = ""
    for i in range(1, instance_count + 1):
        exporter = f"""
  rabbitmq-exporter-{i}:
    image: kbudde/rabbitmq-exporter:latest
    container_name: rabbitmq-exporter-{i}
    environment:
      - RABBIT_URL=http://rabbitmq-{i}:15672
      - RABBIT_USER={rabbitmq_user}
      - RABBIT_PASSWORD={rabbitmq_pass}
    ports:
      - "{9419 + i - 1}:9419"
    networks:
      - esnet
    depends_on:
      - rabbitmq-{i}
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
    deploy:
      resources:
        limits:
          memory: {kibana_memory}
          cpus: "{kibana_cpus}"
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
    deploy:
      resources:
        limits:
          memory: {redis_memory}
          cpus: "{redis_cpus}"
    command: >
      redis-server 
      --appendonly yes 
      --appendfsync everysec
      --maxmemory 6gb
      --maxmemory-policy allkeys-lru
      --save 900 1
      --save 300 10
      --tcp-keepalive 60
      --io-threads 2
      --io-threads-do-reads yes
      --activedefrag yes
      --active-defrag-threshold-lower 10
      --active-defrag-threshold-upper 100
      --active-defrag-cycle-min 25
      --active-defrag-cycle-max 75
      --lazyfree-lazy-eviction yes
      --lazyfree-lazy-expire yes
      --lazyfree-lazy-server-del yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

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
    deploy:
      resources:
        limits:
          memory: {hyperion_memory}
          cpus: "{hyperion_cpus}"
    volumes:
      - hyperiondata:/app/hyperiondata
    depends_on:
      - redis
      - {"rabbitmq-1" if amount_of_rabbitmq_instances > 1 else "rabbitmq"}
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
    deploy:
      resources:
        limits:
          memory: {node_memory}
          cpus: "{node_cpus}"
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
      - "network.host=0.0.0.0"
      - "network.publish_host=es{index}"
      - "transport.host=0.0.0.0"
      - "node.roles=[master, data, ingest, remote_cluster_client]"
      - "ES_JAVA_OPTS=-Xms{min_mem} -Xmx{max_mem} {es_java_opts}"
      - "ES_HEAP_DUMP_PATH={es_heap_dump_path}"
      - "ES_GC_LOG_PATH={es_gc_log_path}"
      - "bootstrap.memory_lock=true"
      - "xpack.security.enabled=false"
      - "xpack.monitoring.collection.enabled=true"
    ports:
      - "127.0.0.1:{http_port}:9200"
      - "127.0.0.1:{transport_port}:9300"
    ulimits:
      memlock:
        soft: -1
        hard: -1
      nofile:
        soft: 65535
        hard: 65535
    volumes:
      - esdata{index}:/usr/share/elasticsearch/data
      - ./elasticsearch/config/es{index}/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml
    networks:
      - esnet
    healthcheck:
      test: ["CMD-SHELL", "curl -s http://localhost:9200/_cluster/health | grep -vq \\\"status\\\":\\\"red\\\""]
      interval: 30s
      timeout: 30s
      retries: 5
      start_period: 60s
"""

# Base for volumes and networks
volumes_and_networks = f"""
volumes:
  grafana-data:
  redisdata:
{generate_rabbitmq_volumes(amount_of_rabbitmq_instances)}
  hyperiondata:
  node:
  certbot-etc:
  certbot-var:
  certbot-www:
{{volumes}}

networks:
  esnet:
"""

# Generate Elasticsearch services
services = ""
initial_master_nodes = ",".join([f"es{i}" for i in range(1, amount_of_nodes + 1)])
seed_hosts = initial_master_nodes

for i in range(1, amount_of_nodes + 1):
    node_config = node_template.format(
        index=i,
        version=elasticsearch_version,
        initial_master_nodes=initial_master_nodes if amount_of_nodes > 1 else "es1",
        seed_hosts=seed_hosts if amount_of_nodes > 1 else "es1",
        min_mem=elastic_min_mem,
        max_mem=elastic_max_mem,
        es_java_opts=es_java_opts,
        es_heap_dump_path=es_heap_dump_path,
        es_gc_log_path=es_gc_log_path,
        http_port=9200 + i - 1,
        transport_port=9300 + i - 1
    )
    services += node_config

# Generate volumes for Elasticsearch
volumes = "\n".join([f"  esdata{i}:" for i in range(1, amount_of_nodes + 1)])

# Define certbot service separately
certbot_service = f"""
  certbot:
    container_name: certbot
    build:
      context: ./certbot
      dockerfile: Dockerfile.certbot
    volumes:
      - certbot-etc:/etc/letsencrypt
      - certbot-var:/var/lib/letsencrypt
      - ./haproxy/certs:/etc/haproxy/certs
      - certbot-www:/var/www/certbot
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - esnet
    environment:
      - CERTBOT_EMAIL={certbot_email}
      - CERTBOT_STAGING={str(certbot_staging).lower()}
      - PRODUCTION_ALIAS_KIBANA={production_alias_kibana}
      - PRODUCTION_ALIAS_GRAFANA={production_alias_grafana}
      - PRODUCTION_ALIAS_HYPERION={production_alias_hyperion}
      - REQUEST_KIBANA_CERT={str(request_kibana_cert).lower()}
      - REQUEST_GRAFANA_CERT={str(request_grafana_cert).lower()}
      - REQUEST_HYPERION_CERT={str(request_hyperion_cert).lower()}
      - FORCE_RENEWAL=true
    depends_on:
      - haproxy
"""

# Update haproxy service with certbot integration
haproxy_service = f"""
  haproxy:
    image: haproxy:2.8-alpine
    container_name: haproxy
    ports:
      - "{haproxy_http_port}:80"
      - "{haproxy_https_port}:443"
    volumes:
      - ./haproxy/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro
      - ./haproxy/certs:/etc/haproxy/certs:ro
      - certbot-www:/var/www/certbot:ro
    depends_on:
      - hyperion
      - kibana
      - grafana
    networks:
      - esnet
    deploy:
      resources:
        limits:
          memory: {haproxy_memory}
          cpus: "{haproxy_cpus}"
    healthcheck:
      test: ["CMD", "haproxy", "-c", "-f", "/usr/local/etc/haproxy/haproxy.cfg"]
      interval: 30s
      timeout: 10s
      retries: 3
"""

# Combine everything
all_services = base_compose + generate_rabbitmq_cluster_services(amount_of_rabbitmq_instances, rabbitmq_cluster_name, rabbitmq_erlang_cookie, rabbitmq_user, rabbitmq_pass, rabbitmq_vhost, rabbitmq_memory, rabbitmq_cpus) + services
if monitoring_enabled:
    all_services += monitoring_services + generate_es_exporters(amount_of_nodes) + generate_rabbitmq_exporters(amount_of_rabbitmq_instances)
if proxy_enabled:
    all_services += haproxy_service
    if certbot_enabled:
        all_services += certbot_service

# Combine services with volumes and networks
volumes_section = volumes_and_networks.format(volumes=volumes)

final_compose = all_services + volumes_section

# Write to docker-compose.yml
with open("docker-compose-generated-hyperion.yml", "w") as f:
    f.write(final_compose)

print(f"Generated docker-compose-generated-hyperion.yml with {amount_of_nodes} Elasticsearch nodes and {amount_of_rabbitmq_instances} RabbitMQ instances.")

def update_prometheus_config(node_count):
    if not monitoring_enabled:
        print("Monitoring disabled, skipping prometheus config update.")
        return
        
    # Read the existing prometheus.yml
    with open("prometheus/hyperion/prometheus.yml", "r") as f:
        config = f.readlines()

    # Generate new elasticsearch_exporter job configuration
    new_es_job = f"""  - job_name: elasticsearch_exporter
    scrape_interval: 1s
    static_configs:
      - targets: {[f'elasticsearch-exporter-{i}:9114' for i in range(1, node_count + 1)]}\n"""

    # Remove any existing elasticsearch_exporter job
    new_config = []
    skip_section = False
    for line in config:
        if 'job_name: elasticsearch_exporter' in line:
            skip_section = True
            continue
        if skip_section:
            if line.strip().startswith('- job_name:'):
                skip_section = False
            else:
                continue
        if not skip_section:
            new_config.append(line)

    # Find the position to insert the new job (before the last job)
    insert_position = None
    for i, line in enumerate(new_config):
        if 'job_name: nodeos_custom_exporter' in line:
            insert_position = i
            break

    if insert_position is not None:
        # Insert the new elasticsearch_exporter job configuration
        new_config.insert(insert_position, new_es_job)
    else:
        # If we didn't find the position, append to the end of scrape_configs
        new_config.append(new_es_job)

    # Write the updated configuration back to the file
    with open("prometheus/hyperion/prometheus.yml", "w") as f:
        f.writelines(new_config)

def update_prometheus_rabbitmq_config(rabbitmq_count):
    """Update Prometheus configuration to include RabbitMQ cluster monitoring"""
    if not monitoring_enabled:
        return
        
    # Read the existing prometheus.yml
    with open("prometheus/hyperion/prometheus.yml", "r") as f:
        config = f.readlines()

    # Generate RabbitMQ exporter job configuration
    if rabbitmq_count == 1:
        new_rabbitmq_job = """  - job_name: rabbitmq_exporter
    scrape_interval: 15s
    static_configs:
      - targets: ['rabbitmq-exporter:9419']\n"""
    else:
        targets = [f'rabbitmq-exporter-{i}:9419' for i in range(1, rabbitmq_count + 1)]
        new_rabbitmq_job = f"""  - job_name: rabbitmq_exporter
    scrape_interval: 15s
    static_configs:
      - targets: {targets}\n"""

    # Remove any existing rabbitmq_exporter job
    new_config = []
    skip_section = False
    for line in config:
        if 'job_name: rabbitmq_exporter' in line:
            skip_section = True
            continue
        if skip_section:
            if line.strip().startswith('- job_name:'):
                skip_section = False
            else:
                continue
        if not skip_section:
            new_config.append(line)

    # Find the position to insert the new job (before the last job)
    insert_position = None
    for i, line in enumerate(new_config):
        if 'job_name: nodeos_custom_exporter' in line:
            insert_position = i
            break

    if insert_position is not None:
        # Insert the new rabbitmq_exporter job configuration
        new_config.insert(insert_position, new_rabbitmq_job)
    else:
        # If we didn't find the position, append to the end of scrape_configs
        new_config.append(new_rabbitmq_job)

    # Write the updated configuration back to the file
    with open("prometheus/hyperion/prometheus.yml", "w") as f:
        f.writelines(new_config)

# Add this line at the end of the script, after writing the docker-compose file
update_prometheus_config(amount_of_nodes)
update_prometheus_rabbitmq_config(amount_of_rabbitmq_instances)
if monitoring_enabled:
    print(f"Updated prometheus.yml with {amount_of_nodes} elasticsearch-exporter targets and {amount_of_rabbitmq_instances} rabbitmq-exporter targets.")
else:
    print("Monitoring disabled, prometheus.yml not updated.")

# Call the setup function at the end of your script
setup_elasticsearch_config(amount_of_nodes)
setup_rabbitmq_cluster_config(amount_of_rabbitmq_instances)
setup_rabbitmq_haproxy_config(amount_of_rabbitmq_instances, rabbitmq_user, rabbitmq_pass)
if proxy_enabled:
    setup_haproxy_config()
    if certbot_enabled:
        # Create certbot directory structure
        os.makedirs("certbot", exist_ok=True)
        print("Certbot configuration created. Certificates will be automatically generated on startup.")
    else:
        print("HAProxy configuration created. Please add your SSL certificates to haproxy/certs/server.pem")

def setup_haproxy_config():
    import os
    from urllib.parse import urlparse
    
    # Create haproxy directories
    os.makedirs("haproxy", exist_ok=True)
    os.makedirs("haproxy/certs", exist_ok=True)
    
    # Extract hostnames from the production aliases (remove protocol)
    kibana_hostname = ""
    grafana_hostname = ""
    hyperion_hostname = ""
    
    if production_alias_kibana:
        parsed_url = urlparse(production_alias_kibana)
        kibana_hostname = parsed_url.netloc or "autobuilds-kibana.oiac.io"
    else:
        kibana_hostname = "autobuilds-kibana.oiac.io"
    
    if production_alias_grafana:
        parsed_url = urlparse(production_alias_grafana)
        grafana_hostname = parsed_url.netloc or "autobuilds-grafana.oiac.io"
    else:
        grafana_hostname = "autobuilds-grafana.oiac.io"
    
    if production_alias_hyperion:
        parsed_url = urlparse(production_alias_hyperion)
        hyperion_hostname = parsed_url.netloc or "autobuilds-hyperion.oiac.io"
    else:
        hyperion_hostname = "autobuilds-hyperion.oiac.io"
    
    # Create haproxy.cfg with proper certbot integration
    haproxy_cfg = f"""global
    log /dev/log local0
    maxconn 4096
    user haproxy
    group haproxy
    daemon
    ssl-default-bind-options no-sslv3 no-tlsv10 no-tlsv11

defaults
    log     global
    mode    http
    option  httplog
    option  dontlognull
    option  forwardfor
    timeout connect 5000
    timeout client  50000
    timeout server  50000
    errorfile 400 /usr/local/etc/haproxy/errors/400.http
    errorfile 403 /usr/local/etc/haproxy/errors/403.http
    errorfile 408 /usr/local/etc/haproxy/errors/408.http
    errorfile 500 /usr/local/etc/haproxy/errors/500.http
    errorfile 502 /usr/local/etc/haproxy/errors/502.http
    errorfile 503 /usr/local/etc/haproxy/errors/503.http
    errorfile 504 /usr/local/etc/haproxy/errors/504.http

frontend http-in
    bind *:80
    mode http
    
    # ACME challenge handling
    acl is_acme_challenge path_beg /.well-known/acme-challenge/
    use_backend certbot if is_acme_challenge
    
    # Redirect all other HTTP traffic to HTTPS
    redirect scheme https code 301 if !is_acme_challenge

frontend https-in
    bind *:443 ssl crt /etc/haproxy/certs/ strict-sni
    mode http
    
    # Host-based routing
    acl host_kibana hdr(host) -i {kibana_hostname}
    acl host_grafana hdr(host) -i {grafana_hostname}
    acl host_hyperion hdr(host) -i {hyperion_hostname}
    
    use_backend kibana_backend if host_kibana
    use_backend grafana_backend if host_grafana
    use_backend hyperion_backend if host_hyperion
    
    # Default backend
    default_backend grafana_backend

backend certbot
    mode http
    server certbot certbot:80 check resolvers docker init-addr none

backend hyperion_backend
    mode http
    balance roundrobin
    option forwardfor
    option httpchk GET /api/status
    http-check expect status 200
    http-request set-header X-Forwarded-Port %[dst_port]
    http-request add-header X-Forwarded-Proto https if {{ ssl_fc }}
    server hyperion hyperion:7000 check inter 2s rise 2 fall 3

backend kibana_backend
    mode http
    balance roundrobin
    option forwardfor
    option httpchk GET /api/status
    http-check expect status 200
    http-request set-header X-Forwarded-Port %[dst_port]
    http-request add-header X-Forwarded-Proto https if {{ ssl_fc }}
    server kibana kibana:5601 check inter 2s rise 2 fall 3

backend grafana_backend
    mode http
    balance roundrobin
    option forwardfor
    option httpchk GET /api/health
    http-check expect status 200
    http-request set-header X-Forwarded-Port %[dst_port]
    http-request add-header X-Forwarded-Proto https if {{ ssl_fc }}
    server grafana grafana:3000 check inter 2s rise 2 fall 3

resolvers docker
    nameserver dns 127.0.0.11:53
    resolve_retries 3
    timeout retry 1s
    hold valid 10s
"""
    
    # Write the haproxy.cfg file
    with open("haproxy/haproxy.cfg", "w") as f:
        f.write(haproxy_cfg)