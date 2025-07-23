#!/bin/bash
set -e

HARBOR_HOSTNAME="${HARBOR_HOSTNAME:-harbor-test.oiac.io}"
NAMESPACE="${NAMESPACE:-harbor}"
TLS_CERT_PATH="${TLS_CERT_PATH:-/etc/letsencrypt/live/$HARBOR_HOSTNAME/fullchain.pem}"
TLS_KEY_PATH="${TLS_KEY_PATH:-/etc/letsencrypt/live/$HARBOR_HOSTNAME/privkey.pem}"
HARBOR_ADMIN_PASSWORD="${HARBOR_ADMIN_PASSWORD:-Harbor123!}"

echo "=== Adding Harbor Helm repo ==="
helm repo add harbor https://helm.goharbor.io || true
helm repo update

echo "=== Creating namespace '$NAMESPACE' if it does not exist ==="
kubectl get namespace "$NAMESPACE" >/dev/null 2>&1 || kubectl create namespace "$NAMESPACE"

echo "=== Creating or updating Harbor ingress TLS secret ==="
if kubectl -n "$NAMESPACE" get secret harbor-tls >/dev/null 2>&1; then
  echo "Secret harbor-tls already exists, replacing..."
  kubectl -n "$NAMESPACE" delete secret harbor-tls
fi
kubectl -n "$NAMESPACE" create secret tls harbor-tls \
  --cert="$TLS_CERT_PATH" \
  --key="$TLS_KEY_PATH"

echo "=== Installing or upgrading Harbor ==="
if helm -n "$NAMESPACE" list | grep -q harbor; then
  echo "Harbor already installed, upgrading..."
  helm upgrade harbor harbor/harbor \
    --namespace "$NAMESPACE" \
    --set expose.type=ingress \
    --set expose.tls.enabled=true \
    --set expose.ingress.hosts.core="$HARBOR_HOSTNAME" \
    --set expose.ingress.className=nginx \
    --set expose.ingress.secretName=harbor-tls \
    --set externalURL="https://$HARBOR_HOSTNAME" \
    --set harborAdminPassword="$HARBOR_ADMIN_PASSWORD" \
    --set notary.enabled=false \
    --set persistence.enabled=true \
    --set portal.enableAnonymous=true
else
  echo "Installing Harbor..."
  helm install harbor harbor/harbor \
    --namespace "$NAMESPACE" \
    --set expose.type=ingress \
    --set expose.tls.enabled=true \
    --set expose.ingress.hosts.core="$HARBOR_HOSTNAME" \
    --set expose.ingress.className=nginx \
    --set expose.ingress.secretName=harbor-tls \
    --set externalURL="https://$HARBOR_HOSTNAME" \
    --set harborAdminPassword="$HARBOR_ADMIN_PASSWORD" \
    --set notary.enabled=false \
    --set persistence.enabled=true \
    --set portal.enableAnonymous=true
fi

echo "=== Harbor deployment complete! ==="
echo "Harbor UI: https://$HARBOR_HOSTNAME"
echo "Admin password: $HARBOR_ADMIN_PASSWORD"