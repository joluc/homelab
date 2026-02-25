# Spliit Helm Chart

Self-hosted expense splitting application - an open-source alternative to Splitwise.

## Prerequisites

- PostgreSQL database (Spliit requires PostgreSQL)
- Ingress controller (Traefik is used in this setup)

## Configuration

### Required Configuration

Before deploying, you need to configure in your homelab-secrets:

1. **Database URL** - PostgreSQL connection string:
   ```yaml
   env:
     DATABASE_URL: "postgresql://username:password@postgresql.database.svc.cluster.local:5432/spliit"
   ```

2. **Ingress Host**:
   ```yaml
   ingress:
     host: "spliit.yourdomain.com"
   ```

### Database Setup

Create a database for Spliit in your PostgreSQL cluster:

```sql
CREATE DATABASE spliit;
```

The application will automatically run migrations on startup via Prisma.

### Optional Features

Spliit supports optional features that can be enabled via environment variables:

#### Document/Image Uploads
Enable users to attach images to expenses (requires S3-compatible storage):

```yaml
env:
  NEXT_PUBLIC_ENABLE_EXPENSE_DOCUMENTS: "true"
  S3_UPLOAD_KEY: "your-access-key"
  S3_UPLOAD_SECRET: "your-secret-key"
  S3_UPLOAD_BUCKET: "spliit-uploads"
  S3_UPLOAD_REGION: "us-east-1"
  S3_UPLOAD_ENDPOINT: "https://s3.amazonaws.com"  # Optional, for alternative providers
```

#### AI Receipt Scanning
Enable AI-powered receipt text extraction (requires OpenAI API):

```yaml
env:
  NEXT_PUBLIC_ENABLE_RECEIPT_EXTRACT: "true"
  OPENAI_API_KEY: "sk-..."
```

#### AI Category Extraction
Enable automatic expense categorization:

```yaml
env:
  NEXT_PUBLIC_ENABLE_CATEGORY_EXTRACT: "true"
  OPENAI_API_KEY: "sk-..."
```

## Deployment

Deploy using Helm:

```bash
helm install spliit ./kubernetes/apps/spliit
```

Or with ArgoCD, create an Application manifest pointing to this chart.

## Health Checks

The deployment includes health check probes:
- Liveness: `/api/health/liveness`
- Readiness: `/api/health/readiness`

## Resources

- **CPU**: 100m request, 500m limit
- **Memory**: 256Mi request, 512Mi limit

Adjust in `values.yaml` based on your usage.

## Access

Once deployed, access Spliit at the configured ingress host (e.g., `https://spliit.yourdomain.com`).

## Notes

- The application runs database migrations automatically on startup
- No persistent volume is needed as all data is stored in PostgreSQL
- The Docker image is pulled from `ghcr.io/spliit-app/spliit`
