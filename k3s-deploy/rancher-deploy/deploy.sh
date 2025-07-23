#!/bin/bash
set -e

RANCHER_HOSTNAME="${RANCHER_HOSTNAME:-rancher-test.oiac.io}"
NAMESPACE="${NAMESPACE:-cattle-system}"
TLS_CERT_PATH="${TLS_CERT_PATH:-/etc/letsencrypt/live/$RANCHER_HOSTNAME/fullchain.pem}"
TLS_KEY_PATH="${TLS_KEY_PATH:-/etc/letsencrypt/live/$RANCHER_HOSTNAME/privkey.pem}"

echo "=== Adding Rancher Helm repo ==="
helm repo add rancher-latest https://releases.rancher.com/server-charts/latest || true
helm repo update

echo "=== Creating namespace '$NAMESPACE' if it does not exist ==="
kubectl get namespace "$NAMESPACE" >/dev/null 2>&1 || kubectl create namespace "$NAMESPACE"

echo "=== Creating or updating Rancher ingress TLS secret ==="
if kubectl -n "$NAMESPACE" get secret tls-rancher-ingress >/dev/null 2>&1; then
  echo "Secret tls-rancher-ingress already exists, replacing..."
  kubectl -n "$NAMESPACE" delete secret tls-rancher-ingress
fi
kubectl -n "$NAMESPACE" create secret tls tls-rancher-ingress \
  --cert="$TLS_CERT_PATH" \
  --key="$TLS_KEY_PATH"

echo "=== Installing or upgrading Rancher ==="
if helm -n "$NAMESPACE" list | grep -q rancher; then
  echo "Rancher already installed, upgrading..."
  helm upgrade rancher rancher-latest/rancher \
    --namespace "$NAMESPACE" \
    --set hostname="$RANCHER_HOSTNAME" \
    --set ingress.ingressClassName=nginx \
    --set replicas=1 \
    --set ingress.tls.source=secret
else
  echo "Installing Rancher..."
  helm install rancher rancher-latest/rancher \
    --namespace "$NAMESPACE" \
    --set hostname="$RANCHER_HOSTNAME" \
    --set ingress.ingressClassName=nginx \
    --set replicas=1 \
    --set ingress.tls.source=secret
fi

echo "=== Rancher deployment complete! ==="