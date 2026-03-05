# Homelab

My self-hosted infrastructure, fully managed with GitOps. Kubernetes (K3s) orchestrates everything, Ansible provisions the nodes, and ArgoCD keeps it all in sync.

## Architecture

```
Internet → Cloudflare → Caddy (Gateway VPS) → K3s (Control Plane VPS)
                                                      ↓
                                              Tailscale Mesh
                                                      ↓
                                              Workers (Raspberry Pis)
```

## Stack

- **Infrastructure**: Ansible, K3s, ArgoCD
- **Networking**: Tailscale, Caddy, Traefik
- **Observability**: Prometheus, Grafana, OpenSearch, Jaeger
- **Security**: UFW, fail2ban, Tailscale ACLs, audit logging

## Structure

```
ansible/          # Node provisioning & K3s setup
kubernetes/
├── infrastructure/   # Core services (ArgoCD, Traefik, MetalLB)
├── observability/    # Monitoring stack
└── apps/             # Applications
```

## Usage

```bash
# 1. Provision nodes
cd ansible
ansible-playbook -i inventory playbooks/01-prepare-nodes.yaml
ansible-playbook -i inventory playbooks/02-setup-tailscale.yaml
ansible-playbook -i inventory playbooks/03-setup-gateway.yaml
ansible-playbook -i inventory playbooks/04-install-k3s.yaml
ansible-playbook -i inventory playbooks/05-install-argocd.yaml

# 2. ArgoCD syncs everything else from this repo
```

## Security

The infrastructure is hardened following security best practices:

- **SSH**: Key-based auth only, root login disabled, fail2ban protection
- **Firewall**: UFW enabled with IP allowlisting
- **Network Isolation**: Tailscale ACLs restrict cross-network access
- **Monitoring**: audit logging, security scanning, intrusion detection

See [docs/SECURITY-REPORT.md](docs/SECURITY-REPORT.md) for the complete security audit and [docs/setup/SECURITY-HARDENING.md](docs/setup/SECURITY-HARDENING.md) for implementation guide.

## Documentation

- **[Security Summary](docs/SECURITY-SUMMARY.md)** - Start here for security overview
- [Security Report](docs/SECURITY-REPORT.md) - Complete security audit
- [Security Hardening Guide](docs/setup/SECURITY-HARDENING.md) - Implementation steps
- [Security Quick Reference](docs/SECURITY-QUICK-REF.md) - Daily checklists
- [Network Architecture](docs/network/README.md)
- [Cloud K3s Setup](docs/setup/CLOUD-K3S-SETUP.md)

## License

MIT
