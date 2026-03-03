# OOM Kill Exporter

Monitors and exports Kubernetes OOM kill events to Prometheus.

## Installation

```bash
cd kubernetes/observability/oomkill-exporter
helm dependency update
helm upgrade --install oomkill-exporter . -n observability
```

## Configuration

See `values.yaml` for configuration options.

## Metrics

- `klog_pod_oomkill` - Counter of OOM kills per pod with labels:
  - `container_name`
  - `namespace`
  - `pod_name`
  - `pod_uid`
