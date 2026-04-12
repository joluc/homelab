# Homelab Architecture Guide

This document helps Claude Code understand the architecture, patterns, and conventions used in this homelab infrastructure.

## Overview

Self-hosted Kubernetes infrastructure running on hybrid cloud setup:
- **Control Plane**: K3s on VPS (16Gi RAM, amd64 — heavy workloads pinned here)
- **Workers**: 5x Raspberry Pi (1x Pi 5, 2x Pi 4, 2x Pi 3) connected via Tailscale
- **Storage**: Synology DS918+ (scheduled 6pm-3am)
- **Management**: GitOps with ArgoCD, Ansible for provisioning

### Hardware Inventory

| Node | Model | Arch | RAM | Storage | Tailscale IP | LAN IP |
|---|---|---|---|---|---|---|
| control-01 | VPS (Delos Cloud) | amd64 | 16 GB | — | 100.97.29.99 | 159.195.63.121 |
| pi-01 | Raspberry Pi 5 Model B Rev 1.0 | aarch64 | 8 GB | 459 GB SSD | — | 192.168.1.192 |
| pi-02 | Raspberry Pi 4 Model B Rev 1.2 | aarch64 | 2 GB | 59 GB SD | — | 192.168.1.184 |
| pi-03 | Raspberry Pi 4 Model B Rev 1.2 | aarch64 | 4 GB | 59 GB SD | — | 192.168.1.47 |
| pi-04 | Raspberry Pi 3 Model B Rev 1.2 | aarch64 | 1 GB | 29 GB SD | — | 192.168.1.175 |
| pi-05 | Raspberry Pi 3 Model B Plus Rev 1.3 | aarch64 | 1 GB | 59 GB SD | — | 192.168.1.209 |

**Notes**: Pi 3 nodes (pi-04, pi-05) have only 1GB RAM — only schedule very lightweight workloads there. All workers run Debian 13 (trixie) aarch64.

## Architecture Patterns

### Network Flow
```
Internet → Cloudflare → Caddy (Gateway VPS) → K3s Control Plane (VPS)
                                                      ↓
                                              Tailscale Mesh
                                                      ↓
                                         Raspberry Pi Workers (5x)
```

### Service Organization
```
kubernetes/
├── infrastructure/   # Core cluster services (ArgoCD, Traefik, OpenBao, Postgres, Redis)
├── observability/    # Monitoring stack (Prometheus, Grafana, OpenSearch, Jaeger, Pyroscope)
└── apps/            # User-facing applications (26+ services)
```

## Key Technologies

### Core Stack
- **Orchestration**: K3s (lightweight Kubernetes)
- **GitOps**: ArgoCD (automatic deployment from git)
- **Ingress**: Traefik (internal routing, HTTP only)
- **Edge Proxy**: Caddy on Gateway VPS (TLS termination)
- **Network Mesh**: Tailscale (secure connectivity)
- **Provisioning**: Ansible

### Authentication & Security
- **Identity Provider**: Pocket ID (OIDC/OAuth2, auth.joluc.de)
- **Service Auth**: OAuth2-Proxy instances (JWT validation)
- **Secrets Management**: OpenBao (Vault fork, vault.joluc.de)
- **Password Manager**: Vaultwarden (Bitwarden-compatible)

### Observability (Signal Lab)
- **Metrics**: Prometheus + Thanos (long-term storage)
- **Visualization**: Grafana (multi-source dashboards) + Perses (GitOps dashboards)
- **Tracing**: Jaeger (distributed tracing) + OpenSearch (trace storage)
- **Profiling**: Pyroscope (continuous profiling)
- **Logs**: OpenSearch (log aggregation and search)
- **Developer Portal**: Backstage (service catalog)

### Data Layer
- **Database**: PostgreSQL (shared, kubernetes/infrastructure/postgres)
- **Cache**: Redis (kubernetes/infrastructure/redis)
- **Object Storage**: Garage S3-compatible (kubernetes/infrastructure/garage)
- **Backups**: K8up (kubernetes/infrastructure/k8up)

### Applications
- **Dashboard**: Homarr (home.joluc.de)
- **Automation**: n8n (workflow automation, n8n.joluc.de)
- **Home Automation**: Home Assistant (ha.joluc.de, hostNetwork enabled for WOL)
- **Photos**: Immich (photos.joluc.de, GPU transcoding)
- **Documents**: Paperless (docs.joluc.de)
- **Notes**: HedgeDoc (notes.joluc.de)
- **DNS**: AdGuard Home (dns.joluc.de, network-wide ad blocking)
- **Network**: UniFi Controller (unifi.joluc.de)
- **Status**: Uptime Kuma (status.joluc.de)
- **Gaming**: Minecraft Java + Bedrock (mc.joluc.de)

## Code Conventions

### Helm Chart Structure
Each service follows this pattern:
```
kubernetes/apps/service-name/
├── Chart.yaml          # Helm chart metadata and dependencies
├── values.yaml         # Service configuration (secrets marked for override)
├── templates/          # Optional custom templates
└── README.md          # Optional service documentation
```

### Values File Pattern
- Sensitive values use placeholder comments: `""  # will be overridden in homelab-secrets`
- Resources always specified with requests and limits
- Ingress uses Traefik IngressClass (`ingressClassName: traefik`)
- Storage uses `local-path` storageClass for local volumes

### Common Patterns
```yaml
# Resource limits (adjust based on service needs)
resources:
  requests:
    cpu: 50m
    memory: 64Mi
  limits:
    cpu: 200m
    memory: 128Mi

# Ingress pattern
ingress:
  enabled: true
  className: traefik
  hosts:
    - host: ""  # will be overridden in homelab-secrets

# Persistence pattern
persistence:
  enabled: true
  storageClass: local-path
  size: 5Gi
```

## Authentication Architecture

### OIDC + JWT Flow
1. User accesses service (e.g., prometheus.joluc.de)
2. OAuth2-Proxy intercepts request
3. Redirects to Pocket ID (auth.joluc.de) if not authenticated
4. Pocket ID issues JWT token after successful login
5. OAuth2-Proxy validates JWT and proxies to upstream service
6. Service receives authenticated requests

### OAuth2-Proxy Pattern
Used to protect observability services:
- `oauth2-proxy/` - Protects Prometheus
- `oauth2-proxy-alertmanager/` - Protects Alertmanager
- `oauth2-proxy-thanos/` - Protects Thanos Query

Common configuration:
```yaml
extraArgs:
  provider: oidc
  oidc-issuer-url: https://auth.joluc.de
  redirect-url: https://service.joluc.de/oauth2/callback
  cookie-secure: true
  cookie-samesite: lax
  email-domain: "*"
  upstream: http://backend-service.namespace.svc:port
```

## Deployment Workflow

### GitOps Process
1. Make changes to YAML files in this repo
2. Commit and push to git
3. ArgoCD automatically detects changes
4. Services are updated/deployed automatically
5. No manual helm/kubectl commands needed

### Infrastructure Setup (Ansible)
```bash
# One-time setup (already done)
ansible-playbook -i inventory playbooks/01-prepare-nodes.yaml
ansible-playbook -i inventory playbooks/02-setup-tailscale.yaml
ansible-playbook -i inventory playbooks/03-setup-gateway.yaml
ansible-playbook -i inventory playbooks/04-install-k3s.yaml
ansible-playbook -i inventory playbooks/05-install-argocd.yaml
```

### Manual Operations
```bash
# Check ArgoCD app status
kubectl get applications -n argocd

# Force sync an application
kubectl patch application apps-homarr -n argocd -p '{"metadata":{"annotations":{"argocd.argoproj.io/refresh":"normal"}}}' --type merge

# View helm releases
helm list -A

# Check pod status
kubectl get pods -A | grep service-name
```

## Resource Allocation Strategy

### Node Selectors
- Heavy/amd64-only workloads: `kubernetes.io/hostname: control-01` (Minecraft, Immich, OpenSearch)
- amd64-only custom images: `kubernetes.io/arch: amd64` (cph-metro-exporter, icebreaker-exporter)
- Default lightweight workloads: `node-role.kubernetes.io/worker: "true"` to spread across Pi workers
- Home Assistant requires `hostNetwork: true` for WOL functionality

### Flannel Networking
- VXLAN overlay runs over Tailscale mesh (`flannel-iface: tailscale0`)
- Control plane `node-ip: 100.97.29.99` (Tailscale IP, not public IP)
- Required so VXLAN tunnels route through Tailscale instead of public internet

### Storage Strategy
- **Local volumes**: `local-path` StorageClass for most services
- **Shared storage**: Synology NAS (scheduled runtime 6pm-3am)
- **Object storage**: Garage S3-compatible for backups and media
- **Database**: Shared PostgreSQL instance for multiple services

### Memory Guidelines
- Lightweight services: 64Mi request, 128Mi limit
- Standard services: 256Mi request, 512Mi limit
- Heavy services: 1Gi+ (OpenSearch 3Gi, Minecraft 2Gi heap/3Gi limit, Immich 2Gi)
- **VPS has 16Gi total** - typically runs at 85-90% memory. Check `kubectl top nodes` before adding heavy services.
- **Pi 3 nodes have 1GB RAM** - only very lightweight services (≤128Mi limit)

## Security Practices

### Network Security
- External traffic → Cloudflare → Caddy (TLS termination) → Traefik (internal routing)
- Tailscale mesh for secure node-to-node communication
- UFW firewall on all nodes
- Fail2ban for SSH protection
- SSH key-based auth only, root login disabled

### Secrets Management
- OpenBao (Vault fork) for secret storage (openbao.joluc.de)
- External Secrets Operator pattern (if implemented)
- Never commit secrets to git (use placeholder comments)
- Secrets injected via environment variables or mounted files

### Authentication
- Pocket ID (OIDC provider) for SSO across services
- OAuth2-Proxy for protecting web UIs
- JWT tokens for stateless authentication
- Admin access to critical services protected by auth

## Common Tasks

### Adding a New Service
1. Create directory: `kubernetes/apps/new-service/`
2. Add `Chart.yaml` with helm dependencies
3. Add `values.yaml` with configuration
4. Mark secrets with override comments
5. Set appropriate resource limits
6. Configure ingress with Traefik
7. Commit and push - ArgoCD handles deployment

### Updating a Service
1. Edit `values.yaml` or `Chart.yaml`
2. Commit and push changes
3. ArgoCD auto-syncs (or manual sync if needed)

### Adding OAuth2 Protection
1. Copy pattern from `kubernetes/observability/oauth2-proxy/`
2. Update service-specific values (redirect-url, upstream)
3. Deploy alongside the service

### Troubleshooting
```bash
# Check pod logs
kubectl logs -n namespace pod-name

# Describe pod for events
kubectl describe pod -n namespace pod-name

# Check ingress configuration
kubectl get ingress -n namespace

# Check ArgoCD sync status
kubectl get application service-name -n argocd -o yaml

# View ArgoCD logs
kubectl logs -n argocd deployment/argocd-application-controller
```

## Resource Links

### Documentation
- [Security Summary](docs/SECURITY-SUMMARY.md) - Security overview
- [Security Report](docs/SECURITY-REPORT.md) - Complete security audit
- [Services Quick Reference](docs/SERVICES-QUICK-REF.md) - All service URLs and configs
- [OpenBao Usage](docs/openbao-usage.md) - Secret management guide
- [Network Architecture](docs/network/README.md) - Network topology and routing

### Important Files
- `ansible/inventory/hosts.yaml` - Infrastructure inventory
- `kubernetes/bootstrap/` - ArgoCD bootstrap configuration
- `.github/workflows/` - CI/CD automation (if present)

## Design Principles

1. **GitOps First**: All changes via git commits, ArgoCD handles deployment
2. **Resource Efficiency**: Optimize for Raspberry Pi constraints (memory, storage)
3. **Observability**: Comprehensive monitoring, tracing, and profiling (Signal Lab)
4. **Security**: Defense in depth (network, application, auth layers)
5. **Simplicity**: Choose lightweight alternatives (Pocket ID over Keycloak)
6. **Documentation**: Keep docs up to date with architecture changes
7. **Automation**: Use n8n for workflow automation, Ansible for provisioning

## Notes for Claude Code

- Always check existing patterns before creating new configurations
- Resource limits are critical due to Raspberry Pi constraints
- Secrets are managed separately - never expose in values.yaml
- Traefik is internal routing only; Caddy on Gateway VPS handles TLS
- Home Assistant needs special `hostNetwork: true` for WOL
- Heavy workloads (OpenSearch, Minecraft, Immich) need node selectors
- ArgoCD is the source of truth for deployments - avoid manual kubectl apply
- When adding auth, follow OAuth2-Proxy pattern from observability services
- All external services should have descriptive URLs (*.joluc.de)
- Consider memory impact when adding new services
