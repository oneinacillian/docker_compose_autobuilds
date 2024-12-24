import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load configurations from environment variables
atomic_environment = os.getenv("ATOMIC_ENVIRONMENT", "testnet")
atomic_launch_on_startup = os.getenv("ATOMIC_LAUNCH_ON_STARTUP", "true")
shiphost = os.getenv("SHIPHOST", "172.168.40.50")
httphost = os.getenv("HTTPHOST", "172.168.40.50")
shipport = os.getenv("SHIPPORT", "29876")
httpport = os.getenv("HTTPPORT", "28888")
postgres_user = os.getenv("POSTGRES_USER", "waxuser")
postgres_password = os.getenv("POSTGRES_PASSWORD", "waxuserpass")
postgres_db = os.getenv("POSTGRES_DB", "atomic")
gf_username = os.getenv("GF_USERNAME", "admin")
gf_password = os.getenv("GF_PASSWORD", "admin123")

# Base Docker Compose configuration
base_compose = f"""
version: '3'

services:
  redis:
    image: "redis:latest"
    container_name: redis
    ports:
      - "6379:6379"
    networks:
      - backend
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
      - backend
    depends_on:
      - redis

  postgres:
    image: postgres:14
    container_name: postgresql
    tty: true
    environment:
      - POSTGRES_USER={postgres_user}
      - POSTGRES_PASSWORD={postgres_password}
      - POSTGRES_DB={postgres_db}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./atomic/Deployment/init-db.sh:/docker-entrypoint-initdb.d/init-db.sh
    networks:
      - backend

  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:latest
    container_name: postgres-exporter
    environment:
      - DATA_SOURCE_NAME=postgresql://{postgres_user}:{postgres_password}@postgres:5432/{postgres_db}?sslmode=disable
    ports:
      - "9187:9187"
    networks:
      - backend
    depends_on:
      - postgres

  atomic:
    container_name: atomic
    tty: true
    build:
      context: ./atomic/Deployment
      dockerfile: Dockerfile.atomic
      args:
        - ATOMIC_ENVIRONMENT={atomic_environment}
        - ATOMIC_LAUNCH_ON_STARTUP={atomic_launch_on_startup}
        - SHIPHOST={shiphost}
        - HTTPHOST={httphost}
        - SHIPPORT={shipport}
        - HTTPPORT={httpport}
        - POSTGRES_USER={postgres_user}
        - POSTGRES_PASSWORD={postgres_password}
        - POSTGRES_DB={postgres_db}
    ports:
      - "9000:9000"
    networks:
      - backend
    volumes:
      - atomic:/app/atomic
    depends_on:
      - postgres
      - redis

  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/atomic/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
      - "--storage.tsdb.path=/prometheus"
      - "--web.console.libraries=/usr/share/prometheus/console_libraries"
      - "--web.console.templates=/usr/share/prometheus/consoles"
    networks:
      - backend

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3030:3000"
    environment:
      - GF_SECURITY_ADMIN_USER={gf_username}
      - GF_SECURITY_ADMIN_PASSWORD={gf_password}
    volumes:
      - ./grafana/provisioning/atomic:/etc/grafana/provisioning
      - grafana_data:/var/lib/grafana
    networks:
      - backend

networks:
  backend:

volumes:
  postgres_data:
  redisdata:
  atomic:
  prometheus_data:
  grafana_data:
"""

# Write to docker-compose-atomic.yml
with open("docker-compose-generated-atomic.yml", "w") as f:
    f.write(base_compose)

print("Generated docker-compose-generated-atomic.yml for Atomic services with monitoring.") 