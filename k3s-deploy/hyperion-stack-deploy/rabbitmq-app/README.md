# RabbitMQ Deployment

RabbitMQ message queue for the Hyperion stack, deployed via ArgoCD.

## Files Overview

### `deployment.yaml`
- **Purpose**: Defines the RabbitMQ container deployment
- **Configuration**: 
  - Uses `rabbitmq:3-management` image
  - Resource limits: 2Gi memory, 1 CPU
  - Health checks using `rabbitmqctl status`
  - Plugin management (disables all, enables management and prometheus)
  - Environment variables for user/password/vhost
  - Configuration file mounts using ConfigMap

### `service.yaml`
- **Purpose**: Exposes RabbitMQ ports
- **Ports**: 
  - 5672 (AMQP)
  - 15672 (Management UI)
  - 15692 (Prometheus metrics)
- **Type**: ClusterIP (internal cluster access)

### `pvc.yaml`
- **Purpose**: Persistent volume claim for RabbitMQ data
- **Storage**: 10Gi using `local-path` storage class
- **Access**: ReadWriteOnce

### `configmap.yaml`
- **Purpose**: Contains RabbitMQ configuration files
- **Contents**: 
  - `rabbitmq.conf`: Main RabbitMQ configuration
  - `rabbitmq-env.conf`: Environment-specific settings
- **Features**:
  - Memory and resource management
  - Queue performance tuning
  - Message handling configuration
  - Management plugin settings

### `kustomization.yaml`
- **Purpose**: Kustomize configuration to manage all RabbitMQ resources

### `application.yaml`
- **Purpose**: ArgoCD application manifest for automated deployment
- **Namespace**: `rabbitmq`
- **Sync Policy**: Automated with self-healing and pruning

## Configuration Details

RabbitMQ is configured with:
- Memory management (40% high watermark)
- Queue performance tuning
- Management plugin enabled
- Prometheus metrics enabled
- Health checks for monitoring

## Access

- **AMQP**: `rabbitmq.rabbitmq.svc.cluster.local:5672`
- **Management UI**: `rabbitmq.rabbitmq.svc.cluster.local:15672`
- **Prometheus Metrics**: `rabbitmq.rabbitmq.svc.cluster.local:15692`
- **From other pods**: `rabbitmq:5672` 