# Atomic App Build

This directory contains the build configuration for the Atomic application.

## Files

- **`Dockerfile`**: Container image definition
- **`entrypoint.sh`**: Container startup script
- **`build.sh`**: Build automation script

## Building the Image

### Prerequisites
- Docker installed and running
- Access to the target container registry

### Quick Build
```bash
cd build
./build.sh
```

### Custom Build
```bash
cd build
IMAGE_NAME=my-atomic IMAGE_TAG=v1.0.0 REGISTRY=my-registry.com PROJECT=myproject ./build.sh
```

### Build and Push
```bash
cd build
PUSH=true ./build.sh
```

## Configuration

The application configuration is now managed through Kubernetes ConfigMaps instead of being built into the image. This allows for:

- **Runtime configuration changes** without rebuilding
- **Environment-specific settings** (dev, staging, prod)
- **Easy updates** through GitOps workflows
- **No image rebuilds** for configuration changes

## Configuration Files

The following configuration files are managed as ConfigMaps:

- `connections.config.json` - Database and service connections
- `server.config.json` - Server settings and API configuration
- `readers.config.json` - Blockchain reader configuration
- `ecosystems.config.json` - PM2 process management

## Customization

### Environment Variables
- `ATOMIC_ENVIRONMENT`: Set to "testnet" or "mainnet"
- `ATOMIC_LAUNCH_ON_STARTUP`: Set to "true" for automatic startup

### Ports
- **9000**: Main HTTP API
- **9001**: Reader service
- **9010**: Metrics endpoint

## Registry Integration

The build script is configured to work with Harbor registry by default:
- Registry: `harbor-test.oiac.io`
- Project: `atomic`
- Image: `atomic:latest`

## Notes

- Configuration changes can be made by updating the ConfigMap in Kubernetes
- The image will automatically use the latest configuration from the ConfigMap
- No need to rebuild the image for configuration updates
- Health checks are configured for ports 9000 (HTTP) and 9001 (Reader)
