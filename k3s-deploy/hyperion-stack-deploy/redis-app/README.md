# Redis Deployment

Redis caching layer for the Hyperion stack, deployed via ArgoCD.

## Files Overview

### `deployment.yaml`
- **Purpose**: Defines the Redis container deployment
- **Configuration**: 
  - Uses `redis:latest` image
  - Resource limits: 2Gi memory, 1 CPU
  - Health checks using `redis-cli ping`
  - All Redis configuration options from Docker Compose preserved
  - Persistent volume mount for data storage

### `service.yaml`
- **Purpose**: Exposes Redis on port 6379
- **Type**: ClusterIP (internal cluster access)

### `pvc.yaml`
- **Purpose**: Persistent volume claim for Redis data
- **Storage**: 10Gi using `local-path` storage class
- **Access**: ReadWriteOnce

### `configmap.yaml`
- **Purpose**: Contains Redis configuration files
- **Contents**: All Redis server options from Docker Compose
  - Memory management (6GB max, LRU eviction)
  - IO threading configuration
  - Active defragmentation settings
  - Lazy freeing options

### `kustomization.yaml`
- **Purpose**: Kustomize configuration to manage all Redis resources

### `application.yaml`
- **Purpose**: ArgoCD application manifest for automated deployment
- **Namespace**: `redis`
- **Sync Policy**: Automated with self-healing and pruning

## Configuration Details

Redis is configured with production-ready settings including:
- Memory management with LRU eviction
- IO threading for better performance
- Active defragmentation
- Lazy freeing for memory optimization
- Health checks for monitoring

## Access

- **Internal**: `redis.redis.svc.cluster.local:6379`
- **From other pods**: `redis:6379` 