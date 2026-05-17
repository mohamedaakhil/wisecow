#!/usr/bin/env bash
# generate-tls-secret.sh
# Generates a self-signed TLS cert and creates a Kubernetes secret.
# Use for local development (Kind / Minikube) only.
# For production, rely on cert-manager + ClusterIssuer.

set -euo pipefail

NAMESPACE="wisecow"
SECRET_NAME="wisecow-tls"
DOMAIN="${1:-wisecow.local}"

echo "Generating self-signed TLS certificate for domain: $DOMAIN"

# Generate private key and self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout tls.key \
  -out    tls.crt \
  -subj   "/CN=${DOMAIN}/O=Wisecow Dev"

# Create or replace the Kubernetes TLS secret
kubectl create secret tls "$SECRET_NAME" \
  --cert=tls.crt \
  --key=tls.key \
  --namespace="$NAMESPACE" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Secret '$SECRET_NAME' created in namespace '$NAMESPACE'."

# Clean up local files
rm -f tls.crt tls.key
echo "Done. Add '$DOMAIN' to your hosts file pointing to: $(minikube ip)"
echo "Windows: Add-Content -Path 'C:\Windows\System32\drivers\etc\hosts' -Value '$(minikube ip)  $DOMAIN'"
