#!/bin/bash
set -e

# Perform all actions as $POSTGRES_USER
export PGUSER="$POSTGRES_USER"
export POSTGRES_DB="atomic"

# Modify postgresql.conf
{ echo; echo "listen_addresses = '*'"; } >> "$PGDATA/postgresql.conf"

# Set shared_buffers and work_mem
total_memory_kb=$(grep MemTotal /proc/meminfo | awk '{print $2}')
shared_buffers_kb=$((total_memory_kb / 4))  # Example: 25% of total memory
echo "shared_buffers = ${shared_buffers_kb}kB" >> "$PGDATA/postgresql.conf"

max_connections=$(sed -n 's/^#*max_connections = \(\S*\).*$/\1/p' $PGDATA/postgresql.conf)
work_mem_kb=$((total_memory_kb / max_connections * 256 / 1000))
sed -i "s/^#*work_mem = .*/work_mem = ${work_mem_kb}kB/" $PGDATA/postgresql.conf
maintenance_work_mem_kb=$((total_memory_kb * 5 / 100))
sed -i "s/^#*maintenance_work_mem = .*/maintenance_work_mem = ${maintenance_work_mem_kb}kB/" $PGDATA/postgresql.conf
effective_cache_size_kb=$((total_memory_kb * 50 / 100))
sed -i "s/^#*effective_cache_size = .*/effective_cache_size = ${effective_cache_size_kb}kB/" $PGDATA/postgresql.conf

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
CREATE EXTENSION IF NOT EXISTS pg_trgm;
EOSQL