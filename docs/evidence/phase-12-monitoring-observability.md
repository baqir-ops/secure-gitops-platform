# Phase 12 — Monitoring & Observability

## 1. Monitoring Stack Health

The Kubernetes monitoring stack was verified in the monitoring namespace.

Verified components:
- Prometheus
- Alertmanager
- Grafana
- Prometheus Operator
- kube-state-metrics
- Prometheus Node Exporter

## 2. Prometheus & Alertmanager

Prometheus and Alertmanager were verified as available and healthy.

Prometheus provides metrics collection and querying for the Kubernetes cluster and application workloads. Alertmanager provides alert management for monitoring rules.

## 3. Prometheus Target Discovery

Prometheus targets were verified through the Prometheus Targets interface.

The up metric was used to validate target availability. A healthy target reports 1.

## 4. Task API ServiceMonitors

Task API monitoring was verified through Kubernetes ServiceMonitor resources for dev, staging and production.

The Task API Prometheus target was verified through the Prometheus Targets interface.

## 5. Prometheus Rules

PrometheusRule resources were verified across the Kubernetes platform.

Existing Task API HTTP 5xx alerting evidence is documented separately in docs/evidence/task-api-http-5xx-alerting.md.

## 6. Monitoring Services

The monitoring namespace was verified for Grafana, Prometheus, Alertmanager, Prometheus Operator, kube-state-metrics and Prometheus Node Exporter.

## 7. Task API Workloads

Task API workloads were verified across development, staging and production environments.

Grafana dashboards were used to observe application and infrastructure metrics.

## 8. Phase 12 Screenshot Evidence

| Screenshot | Evidence |
|---|---|
| phase-12-01-prometheus-targets-up.png | Prometheus target health |
| phase-12-02-prometheus-task-api-target.png | Task API Prometheus target |
| phase-12-03-grafana-request-latency.png | Request rate and latency |
| phase-12-04-grafana-errors-cpu.png | HTTP errors and CPU |
| phase-12-05-grafana-memory-pods.png | Memory and pod metrics |
| phase-12-06-grafana-node-resources.png | Kubernetes node resources |

## 9. Result

Phase 12 monitoring and observability verification was completed.

Prometheus, Alertmanager, Grafana and Kubernetes monitoring components were verified. The Task API was monitored through ServiceMonitor resources, and Grafana provided application and infrastructure observability across the platform environments.

## Evidence Structure

The Phase 12 evidence document is docs/evidence/phase-12-monitoring-observability.md.

Phase 12 screenshots are stored in docs/screenshots/phase-12/.
