# Kibana Deployment

Kibana data visualization interface for the Hyperion stack, deployed via ArgoCD.

## Files Overview

### `deployment.yaml`
- **Purpose**: Defines the Kibana container deployment
- **Configuration**: 
  - Uses `docker.elastic.co/kibana/kibana:8.17.0`
  - Resource limits: 2Gi memory, 1 CPU
  - Environment variables for Elasticsearch connection
  - Health checks using Kibana status API
  - Proper Elasticsearch service discovery

### `service.yaml`
- **Purpose**: Exposes Kibana on port 5601
- **Type**: ClusterIP (internal cluster access)

### `ingress.yaml`
- **Purpose**: Ingress resource for external access
- **Host**: `autobuilds-kibana.oiac.io`
- **TLS**: Disabled (as configured)
- **Annotations**: nginx ingress controller settings

### `kustomization.yaml`
- **Purpose**: Kustomize configuration to manage all Kibana resources

### `application.yaml`
- **Purpose**: ArgoCD application manifest for automated deployment
- **Namespace**: `kibana`
- **Sync Policy**: Automated with self-healing and pruning

## Configuration Details

Kibana is configured to:
- Connect to Elasticsearch using Kubernetes service discovery
- Use the same version as Elasticsearch (8.17.0)
- Provide health checks for monitoring
- Expose via ingress for external access

## Access

- **Internal**: `kibana.kibana.svc.cluster.local:5601`
- **External**: `http://autobuilds-kibana.oiac.io`
- **From other pods**: `kibana:5601`

## Elasticsearch Connection

Kibana connects to Elasticsearch using the Kubernetes service DNS name:
- `http://es1.elasticsearch.svc.cluster.local:9200`

This ensures proper cross-namespace communication between Kibana and Elasticsearch.

## Notes

- No PVC required as Kibana is primarily a web interface
- Ingress provides external access to the Kibana UI
- Health checks ensure Kibana is ready before accepting traffic 