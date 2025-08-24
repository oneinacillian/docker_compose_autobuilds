# Spring Cloud Gateway Deployment

API Gateway for the Hyperion stack providing centralized routing, rate limiting, circuit breaking, and security.

## Files Overview

### `deployment.yaml`
- **Purpose**: Defines the Spring Cloud Gateway container deployment
- **Configuration**: 
  - Uses `openjdk:17-jdk-slim` image
  - Resource limits: 1Gi memory, 500m CPU
  - Health checks using Spring Boot Actuator
  - Environment variables for service discovery
  - Configuration mount using ConfigMap

### `service.yaml`
- **Purpose**: Exposes the gateway on port 8080
- **Type**: ClusterIP (internal cluster access)

### `ingress.yaml`
- **Purpose**: Ingress resource for external access
- **Host**: `api.hyperion.example.com`
- **TLS**: Enabled with secret
- **CORS**: Configured for cross-origin requests

### `configmap.yaml`
- **Purpose**: Contains Spring Cloud Gateway configuration
- **Contents**: `application.yml` with route definitions
- **Features**:
  - Route definitions for all Hyperion services
  - Rate limiting with Redis
  - Circuit breaker patterns
  - Retry mechanisms
  - Health check endpoints

### `kustomization.yaml`
- **Purpose**: Kustomize configuration to manage all gateway resources

### `application.yaml`
- **Purpose**: ArgoCD application manifest for automated deployment
- **Namespace**: `gateway`
- **Sync Policy**: Automated with self-healing and pruning

## API Routes

The gateway provides the following routes:

| Route | Service | Purpose | Rate Limit |
|-------|---------|---------|------------|
| `/hyperion/**` | Hyperion API | Blockchain history API | 100 req/min |
| `/elasticsearch/**` | Elasticsearch | Search and storage | 50 req/min |
| `/kibana/**` | Kibana | Data visualization | 200 req/min |
| `/rabbitmq/**` | RabbitMQ | Message queue management | 30 req/min |
| `/health/**` | Gateway | Health checks | No limit |
| `/docs/**` | Gateway | API documentation | No limit |

## Features

### Rate Limiting
- Uses Redis for distributed rate limiting
- Configurable limits per service
- Burst capacity handling

### Circuit Breaker
- Resilience4j integration
- Automatic fallback responses
- Configurable failure thresholds

### Security
- CORS configuration
- TLS termination
- Request/response logging

### Monitoring
- Spring Boot Actuator endpoints
- Health checks
- Circuit breaker metrics

## Access

- **Internal**: `spring-gateway.gateway.svc.cluster.local:8080`
- **External**: `https://api.hyperion.example.com`
- **Health Check**: `https://api.hyperion.example.com/actuator/health`

## Service Dependencies

The gateway connects to:
- **Redis**: For rate limiting
- **Hyperion**: API endpoints
- **Elasticsearch**: Search endpoints
- **Kibana**: UI endpoints
- **RabbitMQ**: Management endpoints

## Configuration

### Rate Limiting
```yaml
redis-rate-limiter.replenishRate: 100  # requests per second
redis-rate-limiter.burstCapacity: 200   # burst capacity
```

### Circuit Breaker
```yaml
sliding-window-size: 10
failure-rate-threshold: 50
wait-duration-in-open-state: 10s
```

## Notes

- Uses Spring Cloud Gateway for reactive routing
- Integrates with Redis for distributed rate limiting
- Provides circuit breaker patterns for resilience
- Supports service discovery via Kubernetes services
- Includes comprehensive monitoring and health checks 