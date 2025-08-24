#!/bin/bash
set -e

# Build script for Atomic App
echo "Building Atomic App Docker image..."

# Set default values
IMAGE_NAME="${IMAGE_NAME:-atomic}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
REGISTRY="${REGISTRY:-harbor-test.oiac.io}"
PROJECT="${PROJECT:-atomic}"

# Build the image
echo "Building image: ${REGISTRY}/${PROJECT}/${IMAGE_NAME}:${IMAGE_TAG}"
docker build -t "${REGISTRY}/${PROJECT}/${IMAGE_NAME}:${IMAGE_TAG}" .

# Push to registry if PUSH is set to true
if [ "${PUSH:-false}" = "true" ]; then
    echo "Pushing image to registry..."
    docker push "${REGISTRY}/${PROJECT}/${IMAGE_NAME}:${IMAGE_TAG}"
    echo "Image pushed successfully!"
else
    echo "Image built successfully. Set PUSH=true to push to registry."
fi

echo "Build completed!"
