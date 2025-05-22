#!/bin/bash
set -e

# This script is called by certbot after successful certificate renewal
# If RENEWED_DOMAIN and RENEWED_LINEAGE are not set, we'll find and deploy all certificates

deploy_cert() {
    local domain=$1
    local cert_path=$2
    
    echo "Deploying certificate for $domain"
    
    # Combine the certificate and key for HAProxy
    cat "$cert_path/fullchain.pem" \
        "$cert_path/privkey.pem" \
        > "/etc/haproxy/certs/$domain.pem"
    
    chmod 644 "/etc/haproxy/certs/$domain.pem"
    echo "Certificate deployed for $domain"
}

if [ -n "$RENEWED_DOMAIN" ] && [ -n "$RENEWED_LINEAGE" ]; then
    # If variables are set, deploy the specific certificate
    deploy_cert "$RENEWED_DOMAIN" "$RENEWED_LINEAGE"
else
    # If variables are not set, find and deploy all certificates
    echo "Environment variables not set, deploying all certificates..."
    for domain_dir in /etc/letsencrypt/live/*; do
        if [ -d "$domain_dir" ] && [ ! -L "$domain_dir" ]; then
            domain=$(basename "$domain_dir")
            if [[ "$domain" != "README" ]]; then
                deploy_cert "$domain" "$domain_dir"
            fi
        fi
    done
fi

# Reload HAProxy
echo "Reloading HAProxy configuration..."
docker kill --signal=HUP haproxy 2>/dev/null || true
echo "HAProxy reload signal sent" 