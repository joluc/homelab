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

## License

MIT
