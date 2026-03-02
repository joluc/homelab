#!/bin/bash
set -e

# Configuration
IMAGE_NAME="openclaw-custom"
IMAGE_TAG="2026.2.25-kubectl"
REGISTRY="159.195.63.121:5000"  # Adjust if you have a different registry

# Full image reference
FULL_IMAGE="${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "Building custom OpenClaw image..."
cd "$(dirname "$0")"

# Build the image
docker build -t "${FULL_IMAGE}" .

echo "Pushing image to registry..."
docker push "${FULL_IMAGE}"

echo "✓ Image built and pushed: ${FULL_IMAGE}"
echo ""
echo "Next steps:"
echo "1. Update values.yaml to use the custom image"
echo "2. Apply the changes: helm upgrade krabbe . -n openclaw"
echo "3. Wait for the pod to restart"
echo "4. Run: kubectl exec -it -n openclaw <pod-name> -- openclaw onboard --auth-choice openai-codex"
