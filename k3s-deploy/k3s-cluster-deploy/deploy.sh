#!/bin/bash
set -e

CLUSTER_NAME="${CLUSTER_NAME:-demo-cluster}"
AGENTS="${AGENTS:-2}"
KUBECTL_BIN="${KUBECTL_BIN:-/usr/local/bin/kubectl}"

echo "=== Checking for k3d ==="
if ! command -v k3d &> /dev/null; then
  echo "k3d not found, installing..."
  curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
else
  echo "k3d already installed."
fi

echo "=== Checking for kubectl ==="
if ! command -v kubectl &> /dev/null; then
  echo "kubectl not found, installing..."
  curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
  chmod +x kubectl
  mv kubectl "$KUBECTL_BIN"
else
  echo "kubectl already installed."
fi

echo "=== Checking for k3d cluster '$CLUSTER_NAME' ==="
if k3d cluster list | grep -q "$CLUSTER_NAME"; then
  echo "Cluster '$CLUSTER_NAME' already exists."
else
  echo "Creating k3d cluster '$CLUSTER_NAME'..."
  k3d cluster create "$CLUSTER_NAME" \
    --agents "$AGENTS" \
    --port 8080:80@loadbalancer \
    --port 8443:443@loadbalancer \
    --volume /data/k3d-storage:/data@server:0 \
    --volume /data/k3d-storage:/data@agent:0 \
    --volume /data/k3d-storage:/data@agent:1 \
    --k3s-arg "--disable=traefik@server:0"
fi

echo "=== Setting up ingress-nginx Helm repo ==="
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx || true
helm repo update

echo "=== Checking for ingress-nginx controller ==="
if helm list -n ingress-nginx | grep -q ingress-nginx; then
  echo "ingress-nginx already installed."
else
  echo "Installing ingress-nginx controller..."
  helm install nginx ingress-nginx/ingress-nginx \
    --namespace ingress-nginx --create-namespace \
    --set controller.service.type=LoadBalancer
fi

echo "=== All done! ==="

  
