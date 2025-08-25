# Atomic App

Main Atomic application deployment for the Atomic stack.

## Overview

This component deploys the Atomic application with:
- Database connectivity to PostgreSQL
- Redis caching support
- Persistent storage
- Health monitoring
- Environment-specific configuration
- **ConfigMap-based configuration** (no image rebuilds needed)

## Configuration

- **Image**: `atomic:latest` (built from `build/` directory)
- **Ports**: 
  - 9000 (HTTP API)
  - 9001 (Reader service)
  - 9010 (Metrics)
- **Storage**: 10Gi persistent volume
- **Memory**: 4Gi limit, 2Gi request
- **CPU**: 2 core limit, 1 core request

## Environment Variables

### Application Settings
- `ATOMIC_ENVIRONMENT`: testnet
- `ATOMIC_LAUNCH_ON_STARTUP`: true
- `NODE_ENV`: production

## Configuration Management

The application now uses **ConfigMaps** instead of hardcoded configuration:

### ConfigMap Files
- **`connections.config.json`**: Database and service connections
- **`server.config.json`**: Server settings and API configuration  
- **`readers.config.json`**: Blockchain reader configuration
- **`ecosystems.config.json`**: PM2 process management

### Benefits
- ✅ **No image rebuilds** for configuration changes
- ✅ **Runtime updates** through Kubernetes
- ✅ **GitOps workflow** integration
- ✅ **Environment-specific** configurations
- ✅ **Easy rollbacks** and version control

## Health Checks

- **Liveness Probe**: HTTP GET /health every 30s
- **Readiness Probe**: HTTP GET /ready every 10s

## Dependencies

- `local-path` storage class
- Redis service (`redis.redis.svc.cluster.local:6379`)
- PostgreSQL service (`postgres.postgres.svc.cluster.local:5432`)

## Build Process

The application image is built from the `build/` directory:

```bash
cd build
./build.sh                    # Build locally
PUSH=true ./build.sh         # Build and push to registry
```

### Build Customization
```bash
IMAGE_NAME=my-atomic \
IMAGE_TAG=v1.0.0 \
REGISTRY=my-registry.com \
PROJECT=myproject \
./build.sh
```

## Usage

The Atomic service is accessible within the cluster at:
- **HTTP API**: `atomic:9000`
- **Reader Service**: `atomic:9001`
- **Metrics**: `atomic:9010`

## Configuration Updates

To update configuration:

1. **Edit the ConfigMap** in Kubernetes
2. **Restart the deployment** (or use rolling update)
3. **No image rebuild required**

Example:
```bash
kubectl edit configmap atomic-config -n atomic
kubectl rollout restart deployment/atomic -n atomic
```

## ArgoCD Deployment

This service includes an `application.yaml` file for ArgoCD deployment:

### Application Details
- **Name**: `atomic-app`
- **Namespace**: `atomic` (created automatically)
- **Source**: This repository's `atomic-app/` directory
- **Sync Policy**: Automated with pruning and self-healing

### Deploy via ArgoCD
1. **Apply the application** to your ArgoCD instance
2. **ArgoCD will automatically**:
   - Create the `atomic` namespace
   - Deploy the Atomic application with ConfigMap configuration
   - Monitor and maintain the deployment
   - Apply any configuration changes
   - Ensure service dependencies are met

### Manual Deployment (Alternative)
If not using ArgoCD, you can deploy manually:
```bash
kubectl create namespace atomic
kubectl apply -f atomic-app/
```

## Notes

- Ensure Redis and PostgreSQL are running before deploying this component
- The application expects health check endpoints at `/health` and `/ready`
- Configuration changes are applied immediately after pod restart
- The build directory contains Dockerfile, entrypoint script, and build automation
- All configuration is now externalized and manageable through GitOps
- The service is configured for the `atomic` namespace
- Cross-namespace communication with Redis and PostgreSQL services
- Persistent storage ensures data survives pod restarts
- Health checks automatically restart unhealthy containers
