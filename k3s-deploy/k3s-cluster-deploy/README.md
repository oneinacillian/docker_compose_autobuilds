# 🚀 K3s Cluster Deployment

Automated deployment script for setting up a production-ready K3s cluster with ingress capabilities.

## What the `deploy.sh` Script Does

The deployment script automates the following steps:

1. **Installs k3d** (K3s in Docker) for local development
2. **Installs kubectl** for cluster management
3. **Creates a K3s cluster** with:
   - 2 agent nodes for high availability
   - Load balancer ports: 8080 (HTTP) and 8443 (HTTPS)
   - Persistent storage volumes
   - Traefik disabled (we use nginx instead)
4. **Installs nginx-ingress-controller** via Helm for ingress management
5. **Configures the cluster** for production use

## Quickstart

```sh
cd k3s-deploy/k3s-cluster-deploy
./deploy.sh
```

## Cluster Configuration

### Port Mapping
- **HTTP Load Balancer:** `8080:80` (external:internal)
- **HTTPS Load Balancer:** `8443:443` (external:internal)

### Storage
- Persistent volumes mounted to `/data/k3d-storage`
- Available on server and both agent nodes

### Ingress Controller
- **nginx-ingress-controller** installed via Helm
- Service type: `LoadBalancer`
- Automatically handles ingress resources

## HAProxy Frontend Configuration

If you're running HAProxy as a frontend to your K3s cluster, you'll need to configure the backends to point to the K3s load balancer ports.

### HAProxy Backend Configuration Example

```haproxy
# Backend for K3s HTTP traffic
backend k3s_http
    mode http
    balance roundrobin
    server k3s_lb 127.0.0.1:8080 check

# Backend for K3s HTTPS traffic
backend k3s_https
    mode tcp
    balance roundrobin
    server k3s_lb 127.0.0.1:8443 check
```

### Frontend Configuration Example

```haproxy
# HTTP frontend
frontend http_frontend
    bind *:80
    mode http
    default_backend k3s_http

# HTTPS frontend
frontend https_frontend
    bind *:443 ssl crt /path/to/your/cert.pem
    mode tcp
    default_backend k3s_https
```

## Accessing Your Cluster

### Direct Access
- **HTTP:** `http://localhost:8080`
- **HTTPS:** `https://localhost:8443`

### Via HAProxy
- **HTTP:** `http://your-domain.com`
- **HTTPS:** `https://your-domain.com`

## Verification

Check cluster status:
```sh
kubectl cluster-info
kubectl get nodes
kubectl get pods -n ingress-nginx
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```sh
   # Check what's using the ports
   netstat -tlnp | grep :8080
   netstat -tlnp | grep :8443
   ```

2. **Storage Permission Issues**
   ```sh
   # Ensure storage directory exists and has proper permissions
   sudo mkdir -p /data/k3d-storage
   sudo chmod 755 /data/k3d-storage
   ```

3. **Ingress Controller Not Ready**
   ```sh
   # Check ingress controller status
   kubectl get pods -n ingress-nginx
   kubectl describe pod -n ingress-nginx <pod-name>
   ```

### Logs
```sh
# Check k3d logs
k3d cluster logs demo-cluster

# Check ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
```

## Next Steps

After cluster deployment, you can deploy individual services:
- [ArgoCD Deployment](../argo-deploy/README.md)
- [Rancher Deployment](../rancher-deploy/README.md)
- [Harbor Deployment](../harbor-deploy/README.md)
- [Hyperion Stack Deployment](../hyperion-stack-deploy/README.md)