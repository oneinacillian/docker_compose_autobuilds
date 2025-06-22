#!/bin/bash

# RabbitMQ Cluster Deployment Script
# ==================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -i, --instances NUM    Number of RabbitMQ instances (1-5, default: 1)"
    echo "  -m, --memory MEM       Memory per instance (default: 2g)"
    echo "  -c, --cpus CPUS        CPUs per instance (default: 1)"
    echo "  -e, --env FILE         Environment file (default: .env)"
    echo "  -d, --deploy           Deploy the cluster after generation"
    echo "  -s, --status           Show cluster status"
    echo "  -l, --logs             Show RabbitMQ logs"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -i 3 -d                    # Deploy 3-node cluster"
    echo "  $0 -i 5 -m 4g -c 2 -d         # Deploy 5-node cluster with 4GB RAM, 2 CPUs per node"
    echo "  $0 -s                         # Show cluster status"
    echo "  $0 -l                         # Show RabbitMQ logs"
}

# Default values
INSTANCES=1
MEMORY="2g"
CPUS="1"
ENV_FILE=".env"
DEPLOY=false
SHOW_STATUS=false
SHOW_LOGS=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--instances)
            INSTANCES="$2"
            shift 2
            ;;
        -m|--memory)
            MEMORY="$2"
            shift 2
            ;;
        -c|--cpus)
            CPUS="$2"
            shift 2
            ;;
        -e|--env)
            ENV_FILE="$2"
            shift 2
            ;;
        -d|--deploy)
            DEPLOY=true
            shift
            ;;
        -s|--status)
            SHOW_STATUS=true
            shift
            ;;
        -l|--logs)
            SHOW_LOGS=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate inputs
if ! [[ "$INSTANCES" =~ ^[1-5]$ ]]; then
    print_error "Number of instances must be between 1 and 5"
    exit 1
fi

# Check if required files exist
if [[ ! -f "generate_hyperion_compose.py" ]]; then
    print_error "generate_hyperion_compose.py not found. Please run this script from the project root."
    exit 1
fi

# Function to create environment file
create_env_file() {
    print_status "Creating environment file with $INSTANCES RabbitMQ instances..."
    
    cat > "$ENV_FILE" << EOF
# RabbitMQ Cluster Configuration
AMOUNT_OF_RABBITMQ_INSTANCES=$INSTANCES
RABBITMQ_CLUSTER_NAME=hyperion-cluster
RABBITMQ_ERLANG_COOKIE=SWQOKODSQALRPCLNMEQG
RABBITMQ_DEFAULT_USER=rabbitmquser
RABBITMQ_DEFAULT_PASS=rabbitmqpass
RABBITMQ_DEFAULT_VHOST=hyperion
RABBITMQ_MEMORY=$MEMORY
RABBITMQ_CPUS=$CPUS

# Other required variables
AMOUNT_OF_NODE_INSTANCES=1
ELASTICSEARCH_VERSION=8.17.0
ELASTIC_MIN_MEM=15g
ELASTIC_MAX_MEM=15g
KIBANA_VERSION=8.17.0
HYPERION_ENVIRONMENT=testnet
HYPERION_LAUNCH_ON_STARTUP=false
HYPERION_VERSION=3.5.0
MONITORING_ENABLED=true
EOF

    print_success "Environment file created: $ENV_FILE"
}

# Function to generate configuration
generate_config() {
    print_status "Generating Docker Compose configuration..."
    
    if python3 generate_hyperion_compose.py; then
        print_success "Configuration generated successfully"
    else
        print_error "Failed to generate configuration"
        exit 1
    fi
}

# Function to deploy cluster
deploy_cluster() {
    print_status "Deploying RabbitMQ cluster..."
    
    # Stop existing containers if any
    print_status "Stopping existing containers..."
    docker-compose -f docker-compose-generated-hyperion.yml down --remove-orphans 2>/dev/null || true
    
    # Start the cluster
    print_status "Starting RabbitMQ cluster..."
    if docker-compose -f docker-compose-generated-hyperion.yml up -d; then
        print_success "Cluster deployment started"
        
        # Wait for cluster to form
        print_status "Waiting for cluster to form..."
        sleep 30
        
        # Show initial status
        show_cluster_status
    else
        print_error "Failed to deploy cluster"
        exit 1
    fi
}

# Function to show cluster status
show_cluster_status() {
    print_status "Checking cluster status..."
    
    # Check if containers are running
    echo ""
    print_status "Container Status:"
    docker-compose -f docker-compose-generated-hyperion.yml ps | grep rabbitmq || true
    
    # Check cluster status if more than 1 instance
    if [[ $INSTANCES -gt 1 ]]; then
        echo ""
        print_status "Cluster Status:"
        if docker exec rabbitmq-1 rabbitmqctl cluster_status 2>/dev/null; then
            print_success "Cluster is healthy"
        else
            print_warning "Cluster status check failed - nodes may still be starting"
        fi
        
        echo ""
        print_status "Node List:"
        docker exec rabbitmq-1 rabbitmqctl list_nodes 2>/dev/null || print_warning "Node list not available yet"
    fi
    
    # Show access information
    echo ""
    print_status "Access Information:"
    if [[ $INSTANCES -eq 1 ]]; then
        echo "  Management UI: http://localhost:15672"
        echo "  AMQP: localhost:5672"
        echo "  Prometheus: http://localhost:9419"
    else
        echo "  Load Balanced Management UI: http://localhost:15672"
        echo "  Individual Management UIs:"
        for i in $(seq 1 $INSTANCES); do
            echo "    Node $i: http://localhost:$((15672 + i))"
        done
        echo "  Individual Prometheus Exporters:"
        for i in $(seq 1 $INSTANCES); do
            echo "    Node $i: http://localhost:$((9418 + i))"
        done
    fi
    
    echo ""
    print_status "Credentials:"
    echo "  Username: rabbitmquser"
    echo "  Password: rabbitmqpass"
    echo "  Virtual Host: hyperion"
}

# Function to show logs
show_logs() {
    print_status "Showing RabbitMQ logs..."
    
    if [[ $INSTANCES -eq 1 ]]; then
        docker-compose -f docker-compose-generated-hyperion.yml logs -f rabbitmq
    else
        # Show logs from all nodes
        for i in $(seq 1 $INSTANCES); do
            echo ""
            print_status "Logs from rabbitmq-$i:"
            docker-compose -f docker-compose-generated-hyperion.yml logs --tail=20 rabbitmq-$i
        done
        
        echo ""
        print_status "Load balancer logs:"
        docker-compose -f docker-compose-generated-hyperion.yml logs --tail=10 rabbitmq-loadbalancer
    fi
}

# Main execution
main() {
    echo "=========================================="
    echo "  RabbitMQ Cluster Deployment Script"
    echo "=========================================="
    echo ""
    
    if [[ "$SHOW_STATUS" == true ]]; then
        show_cluster_status
        exit 0
    fi
    
    if [[ "$SHOW_LOGS" == true ]]; then
        show_logs
        exit 0
    fi
    
    print_status "Configuration:"
    echo "  Instances: $INSTANCES"
    echo "  Memory per instance: $MEMORY"
    echo "  CPUs per instance: $CPUS"
    echo "  Environment file: $ENV_FILE"
    echo ""
    
    # Create environment file
    create_env_file
    
    # Generate configuration
    generate_config
    
    # Deploy if requested
    if [[ "$DEPLOY" == true ]]; then
        deploy_cluster
    else
        print_status "Configuration generated. To deploy, run:"
        echo "  $0 -i $INSTANCES -m $MEMORY -c $CPUS -d"
        echo ""
        print_status "Or manually deploy with:"
        echo "  docker-compose -f docker-compose-generated-hyperion.yml up -d"
    fi
}

# Run main function
main "$@" 