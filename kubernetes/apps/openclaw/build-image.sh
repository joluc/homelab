#!/bin/bash
set -e

# Configuration
IMAGE_NAME="krabbe"
IMAGE_TAG="2026.4.21"
REGISTRY="joluc"

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
echo "1. Update values.yaml image.tag if needed"
echo "2. Commit and push - ArgoCD handles deployment"
echo "3. Wait for the pod to restart"
echo "4. Run: kubectl exec -it -n openclaw <pod-name> -- openclaw onboard --auth-choice openai-codex"
