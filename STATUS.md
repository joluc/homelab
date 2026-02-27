# Homelab Current Status

**Last Updated**: 2026-02-23
**Session ID**: c7426d63-6adf-4d30-ae58-819bee807b25

## Remote Access
- **SSH**: `ssh root@159.195.63.121`
- Use this to run kubectl commands on the cluster

## Cluster Overview

- **Nodes**: 1 control plane (control-01) - 16GB RAM
- **Memory Usage**: ~50% (freed 5Gi by reducing OpenSearch from 3 to 1 node)
- **Applications**: 25 deployed via ArgoCD
- **K8s Version**: v1.34.4+k3s1

## Recent Fixes (2026-02-23)

- ✅ **N8n**: Fixed PostgreSQL schema permissions - running
- ✅ **Perses**: Fixed image repository - running
- ✅ **Traefik**: Fixed PVC storageClass - running
- ✅ **OpenSearch**: Reduced from 3 nodes to 1 node (freed 5Gi memory)
  - Component: nodes, replicas: 1
  - Roles: cluster_manager, data, ingest
  - Version: 3.5.0 with prometheus exporter
  - Memory: 47% (down from 89%)
- ✅ **Paperless**: Running after deletion and recreation
- ✅ **Prometheus**: Running (manually created CRs, ArgoCD tracks but OutOfSync)
  - Prometheus server running with 50Gi storage
  - Alertmanager running with 5Gi storage
  - Note: ArgoCD admission webhook hook causes sync issues, but pods are operational

## Known Issues

### Remaining Issues
1. **Backstage**: CreateContainerConfigError - needs secret configuration
2. **Openbao**: CreateContainerConfigError - needs openbao-db-creds secret
3. **svclb-traefik**: Pending (traefik loadbalancer)

## Applications Status

Most applications are now healthy. Check with:
```bash
ssh root@159.195.63.121 'kubectl get pods -A | grep -v Running | grep -v Completed'
```

## Quick Commands

```bash
# Access cluster
ssh root@159.195.63.121

# Check all apps
kubectl get application -n argocd

# Check non-running pods
kubectl get pods -A | grep -v Running | grep -v Completed

# Force app sync
kubectl patch application <app-name> -n argocd --type=json \
  -p='[{"op": "replace", "path": "/operation", "value": {"sync": {}}}]'

# Check memory
kubectl top nodes
```
