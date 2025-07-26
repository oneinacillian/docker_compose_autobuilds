# Elasticsearch Deployment

Elasticsearch search and storage engine for the Hyperion stack, deployed via ArgoCD.

## Files Overview

### `deployment.yaml`
- **Purpose**: Defines the Elasticsearch container deployment
- **Configuration**: 
  - Uses `docker.elastic.co/elasticsearch/elasticsearch:8.17.0`
  - Resource limits: 16Gi memory, 4 CPU (to accommodate 15GB heap)
  - Security context for proper file permissions (runAsUser: 1000)
  - Init container to fix permissions on data directory
  - Security capabilities for memory locking (IPC_LOCK, SYS_RESOURCE)
  - Health checks using cluster health API
  - Configuration file mount using ConfigMap

### `service.yaml`
- **Purpose**: Exposes Elasticsearch ports
- **Ports**: 
  - 9200 (HTTP API)
  - 9300 (Transport/Node communication)
- **Type**: ClusterIP (internal cluster access)

### `pvc.yaml`
- **Purpose**: Persistent volume claim for Elasticsearch data
- **Storage**: 50Gi using `local-path` storage class
- **Access**: ReadWriteOnce

### `configmap.yaml`
- **Purpose**: Contains Elasticsearch configuration file
- **Contents**: `elasticsearch.yml` with optimized settings
- **Features**:
  - Memory settings (30% index buffer, 25% fielddata cache)
  - Thread pool configuration
  - Recovery settings
  - Cache and disk settings
  - HTTP settings

### `kustomization.yaml`
- **Purpose**: Kustomize configuration to manage all Elasticsearch resources

### `application.yaml`
- **Purpose**: ArgoCD application manifest for automated deployment
- **Namespace**: `elasticsearch`
- **Sync Policy**: Automated with self-healing and pruning

## Configuration Details

Elasticsearch is configured with production-ready settings including:
- 15GB Java heap size
- Memory locking for performance
- Optimized thread pools
- Recovery and cache settings
- Health checks for monitoring

## Access

- **HTTP API**: `es1.elasticsearch.svc.cluster.local:9200`
- **Transport**: `es1.elasticsearch.svc.cluster.local:9300`
- **From other pods**: `es1:9200`

## Important Notes

- **Memory Requirements**: Needs significant memory (16Gi) for 15GB Java heap
- **Security**: Runs as user 1000 with specific capabilities for memory locking
- **Storage**: 50Gi for data persistence
- **Health Checks**: Uses cluster health API for monitoring 