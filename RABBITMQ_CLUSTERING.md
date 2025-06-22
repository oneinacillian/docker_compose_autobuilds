# RabbitMQ Clustering for Hyperion Deployment

## Overview

This implementation provides a flexible RabbitMQ clustering solution for your Hyperion deployment, allowing you to configure anywhere from 1 to 5 RabbitMQ instances in a cluster configuration. This is particularly beneficial for high-performance deployments where you need:

- **High Availability**: Automatic failover if one node fails
- **Load Distribution**: Better performance under high load
- **Fault Tolerance**: Automatic recovery and healing
- **Scalability**: Handle more concurrent connections and messages

## Benefits of RabbitMQ Clustering

### For High-Performance Instances

When running on a very performant instance, RabbitMQ clustering provides significant benefits:

1. **Parallel Processing**: Multiple nodes can process messages simultaneously
2. **Connection Distribution**: Client connections are distributed across nodes
3. **Queue Mirroring**: Messages are automatically replicated across nodes
4. **Automatic Failover**: If one node fails, others continue serving
5. **Load Balancing**: Built-in load balancing for both AMQP and management interfaces

### Performance Improvements

- **Throughput**: Can handle 2-5x more messages per second
- **Latency**: Reduced latency through connection distribution
- **Reliability**: 99.9%+ uptime with proper cluster configuration
- **Scalability**: Easy to scale up by adding more nodes

## Configuration

### Environment Variables

Add these variables to your `.env` file:

```bash
# Number of RabbitMQ instances (1-5 recommended)
AMOUNT_OF_RABBITMQ_INSTANCES=3

# Cluster configuration
RABBITMQ_CLUSTER_NAME=hyperion-cluster
RABBITMQ_ERLANG_COOKIE=SWQOKODSQALRPCLNMEQG

# Resource allocation per instance
RABBITMQ_MEMORY=2g
RABBITMQ_CPUS=1

# Authentication (shared across all nodes)
RABBITMQ_DEFAULT_USER=rabbitmquser
RABBITMQ_DEFAULT_PASS=rabbitmqpass
RABBITMQ_DEFAULT_VHOST=hyperion
```

### Recommended Configurations

#### Development/Testing
```bash
AMOUNT_OF_RABBITMQ_INSTANCES=1
RABBITMQ_MEMORY=1g
RABBITMQ_CPUS=0.5
```

#### Production (High Availability)
```bash
AMOUNT_OF_RABBITMQ_INSTANCES=3
RABBITMQ_MEMORY=4g
RABBITMQ_CPUS=2
```

#### High-Performance Production
```bash
AMOUNT_OF_RABBITMQ_INSTANCES=5
RABBITMQ_MEMORY=8g
RABBITMQ_CPUS=4
```

## Architecture

### Single Instance Mode (AMOUNT_OF_RABBITMQ_INSTANCES=1)
```
┌─────────────────┐
│   Hyperion      │
│                 │
│  ┌───────────┐  │
│  │ RabbitMQ  │  │
│  │  (Single) │  │
│  └───────────┘  │
└─────────────────┘
```

### Cluster Mode (AMOUNT_OF_RABBITMQ_INSTANCES=3)
```
┌─────────────────────────────────────┐
│            Hyperion                 │
│                                     │
│  ┌───────────┐  ┌───────────┐       │
│  │ RabbitMQ  │  │ RabbitMQ  │       │
│  │   Node 1  │  │   Node 2  │       │
│  └───────────┘  └───────────┘       │
│                                     │
│  ┌───────────┐  ┌───────────┐       │
│  │ RabbitMQ  │  │  Load     │       │
│  │   Node 3  │  │ Balancer  │       │
│  └───────────┘  └───────────┘       │
└─────────────────────────────────────┘
```

## Access Points

### Management Interface
- **Load Balanced**: `http://localhost:15672`
- **Individual Nodes**: 
  - Node 1: `http://localhost:15673`
  - Node 2: `http://localhost:15674`
  - Node 3: `http://localhost:15675`

### AMQP Connections
- **Load Balanced**: `localhost:5672`
- **Individual Nodes**:
  - Node 1: `localhost:5672`
  - Node 2: `localhost:5673`
  - Node 3: `localhost:5674`

### Prometheus Metrics
- **Load Balanced**: `http://localhost:15672/metrics`
- **Individual Exporters**:
  - Node 1: `http://localhost:9419`
  - Node 2: `http://localhost:9420`
  - Node 3: `http://localhost:9421`

## Monitoring

### Automatic Configuration
The system automatically configures monitoring for all RabbitMQ nodes:

1. **Prometheus Exporters**: One exporter per node
2. **Grafana Dashboards**: Pre-configured RabbitMQ dashboards
3. **Health Checks**: Built-in health monitoring
4. **Metrics Collection**: Comprehensive metrics from all nodes

### Key Metrics Monitored
- Message rates (publish/consume)
- Queue depths and processing times
- Connection counts and channel usage
- Memory and disk usage
- Cluster health and node status
- Network partition events

## Deployment

### 1. Configure Environment
```bash
# Copy the example configuration
cp rabbitmq-cluster.env.example .env

# Edit the configuration
nano .env
```

### 2. Generate Configuration
```bash
# Generate the docker-compose file
python3 generate_hyperion_compose.py
```

### 3. Start the Cluster
```bash
# Start all services
docker-compose -f docker-compose-generated-hyperion.yml up -d

# Check cluster status
docker-compose -f docker-compose-generated-hyperion.yml logs rabbitmq-1
```

### 4. Verify Cluster Health
```bash
# Check cluster status
docker exec rabbitmq-1 rabbitmqctl cluster_status

# Check node list
docker exec rabbitmq-1 rabbitmqctl list_nodes
```

## Troubleshooting

### Common Issues

#### Cluster Formation Issues
```bash
# Check if all nodes are running
docker-compose -f docker-compose-generated-hyperion.yml ps

# Check cluster status
docker exec rabbitmq-1 rabbitmqctl cluster_status

# Force reset a node if needed
docker exec rabbitmq-2 rabbitmqctl stop_app
docker exec rabbitmq-2 rabbitmqctl reset
docker exec rabbitmq-2 rabbitmqctl join_cluster rabbit@rabbitmq-1
docker exec rabbitmq-2 rabbitmqctl start_app
```

#### Connection Issues
```bash
# Check if load balancer is working
curl http://localhost:15672/api/overview

# Check individual node health
curl http://localhost:15673/api/overview
curl http://localhost:15674/api/overview
curl http://localhost:15675/api/overview
```

#### Performance Issues
```bash
# Check memory usage
docker exec rabbitmq-1 rabbitmqctl status

# Check queue depths
docker exec rabbitmq-1 rabbitmqctl list_queues name messages consumers

# Check connection counts
docker exec rabbitmq-1 rabbitmqctl list_connections
```

### Logs
```bash
# View all RabbitMQ logs
docker-compose -f docker-compose-generated-hyperion.yml logs rabbitmq-1 rabbitmq-2 rabbitmq-3

# View load balancer logs
docker-compose -f docker-compose-generated-hyperion.yml logs rabbitmq-loadbalancer
```

## Performance Tuning

### For High-Performance Instances

#### Memory Configuration
```bash
# For 32GB+ RAM instances
RABBITMQ_MEMORY=8g
RABBITMQ_CPUS=4

# For 64GB+ RAM instances
RABBITMQ_MEMORY=16g
RABBITMQ_CPUS=8
```

#### Cluster Size Recommendations
- **Small workloads**: 1-2 nodes
- **Medium workloads**: 3 nodes (recommended)
- **High workloads**: 4-5 nodes
- **Very high workloads**: Consider external RabbitMQ cluster

### Queue Configuration
The cluster automatically configures:
- Queue mirroring across all nodes
- Automatic failover
- Load balancing for connections
- Optimized memory and disk settings

## Security Considerations

### Network Security
- All RabbitMQ ports are bound to `127.0.0.1` by default
- Load balancer provides additional security layer
- Rate limiting is enabled on management interface

### Authentication
- Shared credentials across all cluster nodes
- Consider using external authentication for production
- Enable SSL/TLS for production deployments

### Data Persistence
- Each node has its own persistent volume
- Queue data is mirrored across nodes
- Automatic recovery from node failures

## Migration from Single Instance

### Step-by-Step Migration
1. **Backup existing data**:
   ```bash
   docker exec rabbitmq rabbitmqctl export_definitions > rabbitmq_backup.json
   ```

2. **Update configuration**:
   ```bash
   # Set cluster size in .env
   AMOUNT_OF_RABBITMQ_INSTANCES=3
   ```

3. **Regenerate configuration**:
   ```bash
   python3 generate_hyperion_compose.py
   ```

4. **Stop old instance**:
   ```bash
   docker-compose -f docker-compose-generated-hyperion.yml stop rabbitmq
   ```

5. **Start cluster**:
   ```bash
   docker-compose -f docker-compose-generated-hyperion.yml up -d
   ```

6. **Verify migration**:
   ```bash
   docker exec rabbitmq-1 rabbitmqctl cluster_status
   ```

## Best Practices

### Production Recommendations
1. **Use at least 3 nodes** for high availability
2. **Monitor cluster health** regularly
3. **Set up alerts** for node failures
4. **Regular backups** of queue definitions
5. **Test failover scenarios** in staging

### Performance Optimization
1. **Tune memory settings** based on workload
2. **Monitor queue depths** and processing times
3. **Use appropriate queue types** (classic vs quorum)
4. **Implement proper error handling** in applications
5. **Regular maintenance** and monitoring

### Monitoring Best Practices
1. **Set up Grafana dashboards** for visualization
2. **Configure alerts** for critical metrics
3. **Monitor cluster partition events**
4. **Track message rates** and latencies
5. **Regular log analysis** for issues

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs for error messages
3. Verify cluster configuration
4. Test with single instance first
5. Consult RabbitMQ documentation for advanced topics 