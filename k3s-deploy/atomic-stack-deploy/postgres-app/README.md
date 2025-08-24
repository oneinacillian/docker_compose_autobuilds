# PostgreSQL App

PostgreSQL database deployment for the Atomic stack with **fully externalized dynamic configuration**.

## Overview

This component deploys a PostgreSQL 14 database with:
- **Fully externalized configuration** (no hardcoded values in code)
- **Dynamic memory calculation** based on system resources
- **ConfigMap-based parameter management** (postgresql.conf, pg_hba.conf, dynamic-config)
- Persistent storage
- **Runtime parameter updates** without rebuilding
- Health monitoring

## Configuration

- **Image**: `postgres:14`
- **Port**: 5432
- **Storage**: 20Gi persistent volume
- **Memory**: 2Gi limit, 1Gi request
- **CPU**: 1 core limit, 500m request

## Configuration Management

### 🚀 **Fully Externalized Configuration**

All PostgreSQL configuration is now managed through **ConfigMaps** with **zero hardcoded values**:

#### **1. postgresql.conf (postgresql-configmap.yaml)**
- **Base configuration file** with placeholders
- **Dynamic memory settings** calculated at runtime
- **Performance tuning** parameters
- **Extension configuration**

#### **2. pg_hba.conf (pg-hba-configmap.yaml)**
- **Client authentication** rules
- **Network access** control
- **Kubernetes pod** connectivity

#### **3. Dynamic Configuration (dynamic-config-configmap.yaml)**
- **Memory allocation percentages** (25%, 5%, 50%)
- **Work memory multipliers** (256)
- **Connection limits** (100)
- **Extension flags** (pg_trgm)
- **Performance parameters** (checkpoint, logging, autovacuum)

#### **4. init-db.sh (configmap.yaml)**
- **Runtime memory calculation** based on system resources
- **Dynamic parameter application** to postgresql.conf
- **Extension creation** (pg_trgm)

### ✅ **Benefits of Externalized Configuration**

- **Zero hardcoded values** in any code
- **Complete parameter management** through ConfigMaps
- **Runtime memory optimization** based on actual system resources
- **Easy environment-specific** configurations
- **GitOps workflow** integration
- **Immediate rollbacks** and version control

## Dynamic Memory Calculation

The system automatically calculates optimal memory settings based on your configuration:

### **Memory Allocation (Configurable via ConfigMap)**
```yaml
# In dynamic-config-configmap.yaml
shared_buffers_percentage: "25"        # 25% of total system memory
maintenance_work_mem_percentage: "5"   # 5% of total system memory
effective_cache_size_percentage: "50"  # 50% of total system memory
work_mem_multiplier: "256"            # Multiplier for work_mem calculation
```

### **Runtime Calculation (Based on init-db.sh Logic)**
```bash
# These are calculated automatically at runtime
shared_buffers = (total_memory * 25%) / 100
work_mem = (total_memory / max_connections * 256) / 1000
maintenance_work_mem = (total_memory * 5%) / 100
effective_cache_size = (total_memory * 50%) / 100
```

## Configuration Updates

### **Runtime Parameter Changes**

Most parameters can be updated **without restarting**:

```bash
# Update dynamic configuration
kubectl edit configmap postgresql-dynamic-config -n postgres

# Reload configuration (no restart needed)
kubectl exec -n postgres deployment/postgres -- psql -U waxuser -d atomic -c "SELECT pg_reload_conf();"
```

### **Parameters Requiring Restart**

Some parameters require a **full restart**:

```bash
# Update ConfigMap
kubectl edit configmap postgresql-dynamic-config -n postgres

# Restart deployment
kubectl rollout restart deployment/postgres -n postgres
```

### **Parameters That Always Require Restart**
- `shared_buffers` (calculated from shared_buffers_percentage)
- `max_connections`
- `shared_preload_libraries`
- `wal_buffers`
- `checkpoint_segments`

## Configuration Examples

### **Memory Optimization**
```yaml
# In dynamic-config-configmap.yaml
shared_buffers_percentage: "30"        # Increase to 30% of memory
maintenance_work_mem_percentage: "10"  # Increase to 10% of memory
effective_cache_size_percentage: "60"  # Increase to 60% of memory
```

### **Performance Tuning**
```yaml
# In dynamic-config-configmap.yaml
checkpoint_completion_target: "0.9"
random_page_cost: "1.1"               # SSD optimization
effective_io_concurrency: "200"       # Parallel I/O
```

### **Connection Settings**
```yaml
# In dynamic-config-configmap.yaml
max_connections: "200"                 # Increase for high load
enable_pg_trgm: "true"                # Enable text search extension
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PostgreSQL Pod                          │
├─────────────────────────────────────────────────────────────┤
│  Init Container: config-reader                            │
│  ├─ Reads dynamic-config-configmap.yaml                   │
│  ├─ Calculates memory settings                            │
│  └─ Sets environment variables                            │
├─────────────────────────────────────────────────────────────┤
│  Main Container: postgres                                 │
│  ├─ Mounts postgresql.conf (ConfigMap)                    │
│  ├─ Mounts pg_hba.conf (ConfigMap)                       │
│  ├─ Runs init-db.sh (ConfigMap)                          │
│  └─ Applies dynamic configuration                         │
└─────────────────────────────────────────────────────────────┘
```

## Dependencies

- `local-path` storage class
- **ServiceAccount** with ConfigMap read permissions
- **RBAC** rules for configuration access

## Usage

The PostgreSQL service is accessible within the cluster at `postgres:5432`.

## Troubleshooting

### **Check Dynamic Configuration**
```bash
# View current dynamic config
kubectl get configmap postgresql-dynamic-config -n postgres -o yaml

# Check calculated values
kubectl exec -n postgres deployment/postgres -- psql -U waxuser -d atomic -c "SHOW shared_buffers;"
kubectl exec -n postgres deployment/postgres -- psql -U waxuser -d atomic -c "SHOW work_mem;"
```

### **Update Configuration**
```bash
# Edit dynamic configuration
kubectl edit configmap postgresql-dynamic-config -n postgres

# Restart to apply changes
kubectl rollout restart deployment/postgres -n postgres
```

### **Check Init Container Logs**
```bash
# View init container logs
kubectl logs -n postgres deployment/postgres -c config-reader
```

### **Check ConfigMaps**
```bash
# View all ConfigMaps
kubectl get configmaps -n postgres
kubectl describe configmap postgresql-dynamic-config -n postgres
```

## Notes

- **All configuration is externalized** - no hardcoded values anywhere
- **Memory settings are calculated dynamically** based on system resources
- **Easy parameter tuning** through ConfigMap edits
- **Runtime updates** for most parameters
- **Complete GitOps integration** for configuration management
- **Environment-specific** configurations supported
- **Zero code changes** needed for configuration updates
