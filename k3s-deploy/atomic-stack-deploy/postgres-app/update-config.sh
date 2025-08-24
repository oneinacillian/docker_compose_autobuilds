#!/bin/bash
set -e

# PostgreSQL Configuration Update Script
# This script helps update PostgreSQL configuration without rebuilding the image

NAMESPACE="${NAMESPACE:-postgres}"
DEPLOYMENT="${DEPLOYMENT:-postgres}"
USER="${USER:-waxuser}"
DATABASE="${DATABASE:-atomic}"

echo "PostgreSQL Configuration Update Helper"
echo "====================================="

# Function to check if parameter requires restart
requires_restart() {
    local param="$1"
    case "$param" in
        shared_buffers|max_connections|shared_preload_libraries|wal_buffers|checkpoint_segments|max_wal_size|min_wal_size)
            return 0  # Requires restart
            ;;
        *)
            return 1  # Can be reloaded
            ;;
    esac
}

# Function to update a single parameter
update_parameter() {
    local param="$1"
    local value="$2"
    
    echo "Updating parameter: $param = $value"
    
    if requires_restart "$param"; then
        echo "⚠️  Parameter '$param' requires restart to take effect"
        echo "   Update ConfigMap and restart deployment:"
        echo "   kubectl rollout restart deployment/$DEPLOYMENT -n $NAMESPACE"
    else
        echo "🔄 Parameter '$param' can be updated at runtime"
        echo "   Current value: $(kubectl exec -n $NAMESPACE deployment/$DEPLOYMENT -- psql -U $USER -d $DATABASE -t -c "SHOW $param;" | tr -d ' ')"
        
        # Update the parameter
        kubectl exec -n $NAMESPACE deployment/$DEPLOYMENT -- psql -U $USER -d $DATABASE -c "ALTER SYSTEM SET $param = '$value';"
        
        # Reload configuration
        echo "🔄 Reloading configuration..."
        kubectl exec -n $NAMESPACE deployment/$DEPLOYMENT -- psql -U $USER -d $DATABASE -c "SELECT pg_reload_conf();"
        
        echo "✅ Parameter updated successfully!"
        echo "   New value: $(kubectl exec -n $NAMESPACE deployment/$DEPLOYMENT -- psql -U $USER -d $DATABASE -t -c "SHOW $param;" | tr -d ' ')"
    fi
}

# Function to show current configuration
show_config() {
    local param="$1"
    if [ -n "$param" ]; then
        echo "Current value of $param:"
        kubectl exec -n $NAMESPACE deployment/$DEPLOYMENT -- psql -U $USER -d $DATABASE -c "SHOW $param;"
    else
        echo "Current PostgreSQL configuration:"
        kubectl exec -n $NAMESPACE deployment/$DEPLOYMENT -- psql -U $USER -d $DATABASE -c "SHOW ALL;" | head -20
        echo "... (truncated, use 'SHOW ALL;' for full list)"
    fi
}

# Function to reload configuration
reload_config() {
    echo "🔄 Reloading PostgreSQL configuration..."
    kubectl exec -n $NAMESPACE deployment/$DEPLOYMENT -- psql -U $USER -d $DATABASE -c "SELECT pg_reload_conf();"
    echo "✅ Configuration reloaded successfully!"
}

# Function to show help
show_help() {
    echo "Usage: $0 [COMMAND] [PARAMETER] [VALUE]"
    echo ""
    echo "Commands:"
    echo "  show [PARAMETER]     Show current configuration (all or specific parameter)"
    echo "  update PARAM VALUE   Update a specific parameter"
    echo "  reload               Reload configuration from ConfigMap"
    echo "  help                 Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 show                           # Show all configuration"
    echo "  $0 show shared_buffers            # Show specific parameter"
    echo "  $0 update work_mem 8MB            # Update work_mem to 8MB"
    echo "  $0 reload                         # Reload configuration"
    echo ""
    echo "Environment variables:"
    echo "  NAMESPACE  Kubernetes namespace (default: postgres)"
    echo "  DEPLOYMENT Deployment name (default: postgres)"
    echo "  USER       Database user (default: waxuser)"
    echo "  DATABASE   Database name (default: atomic)"
}

# Main script logic
case "${1:-help}" in
    "show")
        show_config "$2"
        ;;
    "update")
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo "❌ Error: Parameter name and value required"
            echo "Usage: $0 update PARAMETER VALUE"
            exit 1
        fi
        update_parameter "$2" "$3"
        ;;
    "reload")
        reload_config
        ;;
    "help"|*)
        show_help
        ;;
esac
