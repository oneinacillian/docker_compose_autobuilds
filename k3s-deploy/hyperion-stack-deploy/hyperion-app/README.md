# Hyperion Deployment

Hyperion History API and Indexer for blockchain data, deployed via ArgoCD.

## Files Overview

### `deployment.yaml`
- **Purpose**: Defines the Hyperion container deployment
- **Configuration**: 
  - Uses `hyperionio/hyperion:3.5.0` image
  - Resource limits: 8Gi memory, 2 CPU
  - Environment variables for configuration
  - Health checks for monitoring
  - Configuration file mounts using ConfigMap
  - Persistent volume mount for data storage

### `service.yaml`
- **Purpose**: Exposes Hyperion ports
- **Ports**: 
  - 7000 (HTTP API)
  - 1234 (Debug/Streaming)
- **Type**: ClusterIP (internal cluster access)

### `pvc.yaml`
- **Purpose**: Persistent volume claim for Hyperion data
- **Storage**: 20Gi using `local-path` storage class
- **Access**: ReadWriteOnce

### `configmap.yaml`
- **Purpose**: Contains Hyperion configuration files
- **Contents**: 
  - `connections.json`: Service connection configuration
  - `wax.config.json`: WAX blockchain configuration
- **Features**:
  - RabbitMQ connection settings
  - Elasticsearch connection settings
  - Redis connection settings
  - WAX chain configuration

### `kustomization.yaml`
- **Purpose**: Kustomize configuration to manage all Hyperion resources

### `application.yaml`
- **Purpose**: ArgoCD application manifest for automated deployment
- **Namespace**: `hyperion`
- **Sync Policy**: Automated with self-healing and pruning

## Configuration Details

Hyperion is configured with:
- Service connections to Redis, RabbitMQ, and Elasticsearch
- WAX blockchain configuration
- API and indexer settings
- Streaming capabilities
- Health checks for monitoring

## Service Dependencies

Hyperion connects to:
- **Redis**: `redis:6379` for caching
- **RabbitMQ**: `rabbitmq:5672` for message queuing
- **Elasticsearch**: `es1:9200` for data storage

## Access

- **HTTP API**: `hyperion.hyperion.svc.cluster.local:7000`
- **Debug/Streaming**: `hyperion.hyperion.svc.cluster.local:1234`
- **From other pods**: `hyperion:7000`

## Configuration Files

### `connections.json`
Contains connection settings for all dependent services:
- AMQP (RabbitMQ) configuration
- Elasticsearch cluster settings
- Redis connection details
- WAX chain configuration

### `wax.config.json`
Contains WAX-specific configuration:
- API settings and limits
- Indexer configuration
- Scaling parameters
- Feature flags
- Performance tuning

## Notes

- Uses ConfigMap for configuration management
- Persistent storage for blockchain data
- Health checks ensure service availability
- Resource limits prevent memory issues 