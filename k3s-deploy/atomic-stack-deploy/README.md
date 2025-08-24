# Atomic Stack Deployment

This directory contains Kubernetes manifests for deploying the Atomic stack using ArgoCD.

## Overview

The Atomic stack consists of three main components:
- **Redis**: In-memory data structure store for caching and session management
- **PostgreSQL**: Primary database for the Atomic application
- **Atomic**: Main application service with **ConfigMap-based configuration**

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Redis    │    │ PostgreSQL  │    │   Atomic   │
│   (6379)   │    │   (5432)    │    │   (9000)   │
└─────────────┘    └─────────────┘    └─────────────┘
```

## Components

### Redis App (`redis-app/`)
- **Deployment**: Redis server with persistence and optimized configuration
- **Service**: ClusterIP service exposing port 6379
- **PVC**: 10Gi persistent storage for Redis data
- **Health Checks**: Liveness and readiness probes using redis-cli ping

### PostgreSQL App (`postgres-app/`)
- **Deployment**: PostgreSQL 14 database server
- **Service**: ClusterIP service exposing port 5432
- **PVC**: 20Gi persistent storage for database data
- **ConfigMap**: Initialization script for database setup
- **Health Checks**: Liveness and readiness probes using pg_isready

### Atomic App (`atomic-app/`)
- **Deployment**: Main Atomic application service
- **Service**: ClusterIP service exposing ports 9000, 9001, 9010
- **PVC**: 10Gi persistent storage for application data
- **ConfigMaps**: All configuration externalized (connections, server, readers, PM2)
- **Build Directory**: Dockerfile, entrypoint script, and build automation
- **Health Checks**: HTTP-based liveness and readiness probes

## Key Features

### 🚀 **ConfigMap-Based Configuration**
- **No image rebuilds** needed for configuration changes
- **Runtime updates** through Kubernetes ConfigMaps
- **GitOps workflow** integration
- **Easy rollbacks** and version control

### 🏗️ **Build Automation**
- **Dockerfile** for container image
- **Entrypoint script** with service dependency checks
- **Build script** with registry integration
- **Harbor registry** support out of the box

## Prerequisites

- Kubernetes cluster with ArgoCD installed
- `local-path` storage class available (for local development)
- Access to the container registry containing the Atomic image
- Docker for building the Atomic application image

## Deployment

### 1. Build Atomic Application
```bash
cd atomic-app/build
./build.sh                    # Build locally
PUSH=true ./build.sh         # Build and push to registry
```

### 2. Deploy Redis
```bash
kubectl apply -f redis-app/
```

### 3. Deploy PostgreSQL
```bash
kubectl apply -f postgres-app/
```

### 4. Deploy Atomic Application
```bash
kubectl apply -f atomic-app/
```

## ArgoCD Applications

Each component has its own ArgoCD application for automated deployment:

- `atomic-redis`: Deploys Redis to the `redis` namespace
- `atomic-postgres`: Deploys PostgreSQL to the `postgres` namespace  
- `atomic-app`: Deploys the Atomic application to the `atomic` namespace

## Configuration

### Environment Variables

The Atomic application is configured with the following environment variables:

- `ATOMIC_ENVIRONMENT`: Set to "testnet"
- `ATOMIC_LAUNCH_ON_STARTUP`: Set to "true"
- `NODE_ENV`: Set to "production"

### Configuration Files (ConfigMaps)

All configuration is now externalized in ConfigMaps:

- **`connections.config.json`**: Database and Redis connections
- **`server.config.json`**: Server settings and API configuration
- **`readers.config.json`**: Blockchain reader configuration
- **`ecosystems.config.json`**: PM2 process management

### Storage

- Redis: 10Gi persistent storage
- PostgreSQL: 20Gi persistent storage
- Atomic: 10Gi persistent storage

All storage uses the `local-path` storage class for local development.

## Health Monitoring

Each service includes:
- **Liveness Probes**: Detect and restart unhealthy containers
- **Readiness Probes**: Ensure traffic is only sent to ready containers
- **Resource Limits**: CPU and memory constraints to prevent resource exhaustion

## Configuration Updates

To update Atomic application configuration:

1. **Edit the ConfigMap** in Kubernetes
2. **Restart the deployment** (or use rolling update)
3. **No image rebuild required**

Example:
```bash
kubectl edit configmap atomic-config -n atomic
kubectl rollout restart deployment/atomic -n atomic
```

## Troubleshooting

### Check Pod Status
```bash
kubectl get pods -n redis
kubectl get pods -n postgres
kubectl get pods -n atomic
```

### Check Service Status
```bash
kubectl get svc -n redis
kubectl get svc -n postgres
kubectl get svc -n atomic
```

### Check PVC Status
```bash
kubectl get pvc -n redis
kubectl get pvc -n postgres
kubectl get pvc -n atomic
```

### View Logs
```bash
kubectl logs -f deployment/redis -n redis
kubectl logs -f deployment/postgres -n postgres
kubectl logs -f deployment/atomic -n atomic
```

### Check ConfigMaps
```bash
kubectl get configmaps -n atomic
kubectl describe configmap atomic-config -n atomic
```

## Notes

- The Atomic application depends on both Redis and PostgreSQL services
- **Configuration changes are applied immediately** after pod restart
- **No image rebuilds needed** for configuration updates
- Ensure proper network policies if running in a multi-tenant cluster
- Consider adjusting resource limits based on your cluster capacity
- The PostgreSQL init script is a placeholder and should be customized for your specific database schema needs
- The build directory contains all necessary files for building and customizing the Atomic image
