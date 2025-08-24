# Redis App

Redis deployment for the Atomic stack.

## Overview

This component deploys a Redis server with:
- Persistence enabled (AOF)
- Memory management (10GB max, LRU eviction)
- Health monitoring
- Persistent storage

## Configuration

- **Image**: `redis:latest`
- **Port**: 6379
- **Storage**: 10Gi persistent volume
- **Memory**: 2Gi limit, 1Gi request
- **CPU**: 1 core limit, 500m request

## Health Checks

- **Liveness Probe**: Redis CLI ping every 10s
- **Readiness Probe**: Redis CLI ping every 5s

## Dependencies

- `local-path` storage class
- No external dependencies

## Usage

The Redis service is accessible within the cluster at `redis:6379`.
