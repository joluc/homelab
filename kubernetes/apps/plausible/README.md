# Plausible Analytics

Privacy-friendly web analytics for your homelab.

## Architecture

This setup uses:
- **Shared PostgreSQL** (in `kubernetes/infrastructure/postgres`) for application data
- **Shared ClickHouse** (in `kubernetes/infrastructure/clickhouse`) for analytics event storage
- **Plausible Analytics** application (this chart)

## Prerequisites

### 1. ClickHouse Infrastructure

ClickHouse must be deployed first as a shared infrastructure component:
- Located at: `kubernetes/infrastructure/clickhouse`
- Uses Bitnami ClickHouse Helm chart (v9.4.4)
- Automatically creates `plausible_events_db` database on initialization

### 2. PostgreSQL Database

The `plausible` database and user should already exist in your shared PostgreSQL instance.

Check `homelab-secrets/kubernetes/infrastructure/postgres/values.yaml` - it should contain:
```sql
CREATE DATABASE plausible;
CREATE USER plausible WITH ENCRYPTED PASSWORD 'plausible';
GRANT ALL PRIVILEGES ON DATABASE plausible TO plausible;
\c plausible
GRANT ALL ON SCHEMA public TO plausible;
ALTER SCHEMA public OWNER TO plausible;
```

## Configuration

### Main Configuration (values.yaml)

The main configuration includes:
- Image version
- Database connection details (pointing to shared services)
- Resource limits
- Persistence configuration

### Secret Configuration (homelab-secrets)

Update the following in `homelab-secrets/kubernetes/apps/plausible/values.yaml`:

1. **Base URL**: Set your domain (e.g., `https://analytics.joluc.de`)
2. **Secret Key Base**: Generate with `openssl rand -base64 64`
3. **PostgreSQL password**: Should match the password in PostgreSQL init script
4. **ClickHouse password**: Should match the password in ClickHouse secrets
5. **Ingress host**: Set your domain

## Deployment Order

ArgoCD will handle deployment, but ensure this order:

1. **ClickHouse** (infrastructure/clickhouse) - deploys first
2. **PostgreSQL** (infrastructure/postgres) - should already exist with plausible database
3. **Plausible** (apps/plausible) - waits for both databases via init containers

## First-Time Setup

After deployment, Plausible will automatically:
- Create database schema in PostgreSQL
- Run migrations
- Start the application

Since registration is set to `invite_only`, you can:

1. Access Plausible at your configured domain (e.g., `https://analytics.joluc.de`)
2. Use the registration form (first user becomes admin)
3. Or create users via the admin panel after initial setup

## Adding Sites

1. Log in to Plausible
2. Click "Add a website"
3. Enter your domain
4. Add the tracking script to your website:
   ```html
   <script defer data-domain="yourdomain.com" src="https://analytics.joluc.de/js/script.js"></script>
   ```

## Service Endpoints

- **Plausible**: `plausible.plausible.svc.cluster.local:8000`
- **ClickHouse**: `clickhouse.clickhouse.svc.cluster.local:8123` (HTTP)
- **PostgreSQL**: `postgres-postgresql.postgres.svc.cluster.local:5432`

## Monitoring

Check deployment status:
```bash
# Check all components
kubectl get pods -n clickhouse
kubectl get pods -n plausible

# Check Plausible logs
kubectl logs -n plausible deployment/plausible

# Check ClickHouse logs
kubectl logs -n clickhouse statefulset/clickhouse-shard0

# Verify database connectivity
kubectl exec -n plausible deployment/plausible -- wget -qO- clickhouse.clickhouse.svc.cluster.local:8123
```

## Storage

- **ClickHouse data**: 20Gi PVC (configured in infrastructure/clickhouse)
- **Plausible GeoIP data**: 1Gi PVC (for IP geolocation database)

## Troubleshooting

### Plausible pod stuck in init
Check if ClickHouse and PostgreSQL are running:
```bash
kubectl get pods -n clickhouse
kubectl get pods -n postgres
```

### Database connection issues
Verify connection strings in ConfigMap:
```bash
kubectl get configmap -n plausible plausible-config -o yaml
```

### Check ClickHouse database
```bash
kubectl exec -n clickhouse statefulset/clickhouse-shard0-0 -- clickhouse-client -q "SHOW DATABASES"
```

## Resources

- Official Docs: https://plausible.io/docs
- GitHub: https://github.com/plausible/analytics
- Docker Hub: https://hub.docker.com/r/plausible/analytics
- Bitnami ClickHouse Chart: https://github.com/bitnami/charts/tree/main/bitnami/clickhouse
