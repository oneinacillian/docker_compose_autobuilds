#!/bin/bash
set -e

# Function to check if a service is ready
check_service() {
    local service=$1
    local port=$2
    local max_attempts=30
    local attempt=1

    echo "Checking if $service is ready..."
    while ! curl -sf "http://$service:$port/api/status" > /dev/null 2>&1; do
        if [ $attempt -ge $max_attempts ]; then
            echo "WARNING: $service not ready after 5 minutes, but proceeding anyway..."
            return 0  # Return success to allow certificate generation to proceed
        fi
        echo "Waiting for $service to be ready (attempt $attempt/$max_attempts)..."
        sleep 10
        attempt=$((attempt + 1))
    done
    echo "$service is ready!"
    return 0
}

# Function to reload HAProxy
reload_haproxy() {
    echo "Reloading HAProxy configuration..."
    # Using Docker to send SIGHUP to HAProxy
    docker kill --signal=HUP haproxy 2>/dev/null || true
    echo "HAProxy reload signal sent"
}

# Function to generate certificates for a domain
generate_cert() {
    local domain=$1
    local email=$2
    local staging=$3
    local service=$4
    local port=$5
    local request_flag=$6
    
    # Check if certificate is requested
    if [ "$request_flag" != "true" ]; then
        echo "Certificate generation for $domain is disabled by configuration"
        return 0
    fi
    
    # Validate inputs
    if [ -z "$domain" ] || [ -z "$email" ]; then
        echo "ERROR: Domain and email are required"
        return 1
    fi
    
    # Create certs directory if it doesn't exist
    mkdir -p /etc/haproxy/certs
    
    # Check if we already have a valid certificate
    if [ -f "/etc/haproxy/certs/$domain.pem" ] && ! [ "$FORCE_RENEWAL" = "true" ]; then
        echo "Certificate for $domain already exists and force renewal not requested"
        return 0
    fi
    
    # Add retry mechanism for certificate generation
    local max_retries=3
    local retry=0
    local staging_arg=""
    
    # Convert staging string to boolean
    if [ "${staging,,}" = "true" ]; then
        staging_arg="--test-cert"
        echo "Using staging environment for certificate generation"
    else
        echo "Using production environment for certificate generation"
    fi
    
    while [ $retry -lt $max_retries ]; do
        echo "Attempting to generate certificate for $domain (attempt $((retry + 1))/$max_retries)"
        certbot certonly --webroot \
            -w /var/www/certbot \
            -d "$domain" \
            --email "$email" \
            --agree-tos --no-eff-email \
            $staging_arg \
            ${FORCE_RENEWAL:+"--force-renewal"} \
            --non-interactive && break
            
        retry=$((retry + 1))
        if [ $retry -lt $max_retries ]; then
            echo "Retry $retry/$max_retries: Certificate generation failed, waiting 30s..."
            sleep 30
        fi
    done

    # If certificate was generated successfully, prepare it for HAProxy
    if [ -d "/etc/letsencrypt/live/$domain" ]; then
        echo "Certificate generated successfully for $domain, preparing for HAProxy..."
        cat "/etc/letsencrypt/live/$domain/fullchain.pem" \
            "/etc/letsencrypt/live/$domain/privkey.pem" \
            > "/etc/haproxy/certs/$domain.pem"
        chmod 644 "/etc/haproxy/certs/$domain.pem"
        echo "Certificate prepared for HAProxy: /etc/haproxy/certs/$domain.pem"
        # Reload HAProxy to pick up the new certificate
        reload_haproxy
    else
        echo "Failed to generate certificate for $domain"
        return 1
    fi
}

# Start the HTTP server for ACME challenges
echo "Starting HTTP server for ACME challenges..."
/opt/serve-http.sh &
HTTP_SERVER_PID=$!

# Initial delay to allow services to start
echo "Initial delay to allow services to start..."
sleep 30

# Generate certificates for each domain
if [ -n "$PRODUCTION_ALIAS_KIBANA" ]; then
    domain=$(echo "$PRODUCTION_ALIAS_KIBANA" | sed 's|https://||')
    generate_cert "$domain" "$CERTBOT_EMAIL" "$CERTBOT_STAGING" "kibana" "5601" "$REQUEST_KIBANA_CERT"
fi

if [ -n "$PRODUCTION_ALIAS_GRAFANA" ]; then
    domain=$(echo "$PRODUCTION_ALIAS_GRAFANA" | sed 's|https://||')
    generate_cert "$domain" "$CERTBOT_EMAIL" "$CERTBOT_STAGING" "grafana" "3000" "$REQUEST_GRAFANA_CERT"
fi

if [ -n "$PRODUCTION_ALIAS_HYPERION" ]; then
    domain=$(echo "$PRODUCTION_ALIAS_HYPERION" | sed 's|https://||')
    generate_cert "$domain" "$CERTBOT_EMAIL" "$CERTBOT_STAGING" "hyperion" "7000" "$REQUEST_HYPERION_CERT"
fi

# Set up automatic renewal
while true; do
    echo "Starting certificate renewal check..."
    renew_args="--webroot -w /var/www/certbot --deploy-hook /opt/deploy-hook.sh"
    
    if [ "$FORCE_RENEWAL" = "true" ]; then
        renew_args="$renew_args --force-renewal"
    fi
    
    if [ "${CERTBOT_STAGING,,}" = "true" ]; then
        renew_args="$renew_args --test-cert"
    fi
    
    certbot renew $renew_args
    echo "Next renewal check in 12 hours..."
    sleep 12h
done 