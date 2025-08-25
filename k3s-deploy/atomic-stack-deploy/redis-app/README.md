# Redis App

Redis deployment for the Atomic stack.

## Overview

This component deploys a Redis server with:
- Persistence enabled (AOF)
- Memory management (10GB max, LRU eviction)
- Health monitoring
- Persistent storage

## Configuration

- **Image**: `redis:latest`
- **Port**: 6379
- **Storage**: 10Gi persistent volume
- **Memory**: 2Gi limit, 1Gi request
- **CPU**: 1 core limit, 500m request

## Health Checks

- **Liveness Probe**: Redis CLI ping every 10s
- **Readiness Probe**: Redis CLI ping every 5s

## Dependencies

- `local-path` storage class
- No external dependencies

## Usage

The Redis service is accessible within the cluster at `redis:6379`.

## ArgoCD Deployment

This service includes an `application.yaml` file for ArgoCD deployment:

### Application Details
- **Name**: `atomic-redis`
- **Namespace**: `redis` (created automatically)
- **Source**: This repository's `redis-app/` directory
- **Sync Policy**: Automated with pruning and self-healing

### Deploy via ArgoCD
1. **Apply the application** to your ArgoCD instance
2. **ArgoCD will automatically**:
   - Create the `redis` namespace
   - Deploy Redis with persistent storage
   - Monitor and maintain the deployment
   - Apply any configuration changes

### Manual Deployment (Alternative)
If not using ArgoCD, you can deploy manually:
```bash
kubectl create namespace redis
kubectl apply -f redis-app/
```

## Notes

- The service is configured for the `redis` namespace
- Persistent storage ensures data survives pod restarts
- Health checks automatically restart unhealthy containers
