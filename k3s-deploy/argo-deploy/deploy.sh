#!/bin/bash
set -e

ARGOCD_HOSTNAME="${ARGOCD_HOSTNAME:-argo-test.oiac.io}"
NAMESPACE="${NAMESPACE:-argocd}"
TLS_CERT_PATH="${TLS_CERT_PATH:-/etc/letsencrypt/live/$ARGOCD_HOSTNAME/fullchain.pem}"
TLS_KEY_PATH="${TLS_KEY_PATH:-/etc/letsencrypt/live/$ARGOCD_HOSTNAME/privkey.pem}"

echo "=== Adding ArgoCD Helm repo ==="
helm repo add argo https://argoproj.github.io/argo-helm || true
helm repo update

echo "=== Creating namespace '$NAMESPACE' if it does not exist ==="
kubectl get namespace "$NAMESPACE" >/dev/null 2>&1 || kubectl create namespace "$NAMESPACE"

echo "=== Creating or updating ArgoCD ingress TLS secret ==="
if kubectl -n "$NAMESPACE" get secret argocd-tls >/dev/null 2>&1; then
  echo "Secret argocd-tls already exists, replacing..."
  kubectl -n "$NAMESPACE" delete secret argocd-tls
fi
kubectl -n "$NAMESPACE" create secret tls argocd-tls \
  --cert="$TLS_CERT_PATH" \
  --key="$TLS_KEY_PATH"

echo "=== Installing or upgrading ArgoCD ==="
if helm -n "$NAMESPACE" list | grep -q argocd; then
  echo "ArgoCD already installed, upgrading..."
  helm upgrade argocd argo/argo-cd \
    --namespace "$NAMESPACE" \
    --set server.ingress.enabled=true \
    --set server.ingress.hostname="$ARGOCD_HOSTNAME" \
    --set server.ingress.ingressClassName=nginx \
    --set server.ingress.tls=true \
    --set server.ingress.tlsSecretName=argocd-tls \
    --set server.extraArgs="{--insecure}" \
    --set configs.params.server\\.insecure=true
else
  echo "Installing ArgoCD..."
  helm install argocd argo/argo-cd \
    --namespace "$NAMESPACE" \
    --set server.ingress.enabled=true \
    --set server.ingress.hostname="$ARGOCD_HOSTNAME" \
    --set server.ingress.ingressClassName=nginx \
    --set server.ingress.tls=true \
    --set server.ingress.tlsSecretName=argocd-tls \
    --set server.extraArgs="{--insecure}" \
    --set configs.params.server\\.insecure=true
fi

echo "=== Waiting for ArgoCD admin secret to be created... ==="
for i in {1..30}; do
  if kubectl -n "$NAMESPACE" get secret argocd-initial-admin-secret >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

echo "=== ArgoCD Initial Admin Password ==="
kubectl -n "$NAMESPACE" get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d; echo

echo "=== ArgoCD deployment complete! ==="