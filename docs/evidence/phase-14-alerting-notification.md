# Phase 14 — Alerting and Notification Flow Evidence

## 1. Phase Objective

Phase 14 validates the Prometheus alerting configuration implemented for the Secure GitOps Platform.

This phase verifies:

- PrometheusRule configuration
- Git desired state
- Kubernetes deployed state
- Prometheus rule evaluation
- Alert state
- High HTTP 5xx alert configuration
- Alert lifecycle evidence
- GitOps consistency
- Evidence screenshot collection

The implemented alerting configuration is based on the Task API high HTTP 5xx error-rate condition.

## 2. Implemented Alert

The implemented Prometheus alert is:

TaskAPIHighHTTP5xxRate

The alert detects when the Task API HTTP 5xx response rate exceeds 5% for 5 consecutive minutes.

Configuration:

- Alert name: TaskAPIHighHTTP5xxRate
- Threshold: greater than 5%
- Evaluation window: 5 minutes
- Alert duration: 5 minutes
- Severity: warning
- Service: task-api

## 3. Git Desired State

The PrometheusRule is defined in:

platform/monitoring/manifests/task-api-alerts.yaml

The repository contains the following alert:

TaskAPIHighHTTP5xxRate

A repository-wide search for TaskApiDown and TaskAPIDown returned no results.

Therefore the deployed alerting configuration matches the current Git desired state.

## 4. Live Kubernetes PrometheusRule

The live Kubernetes resource was inspected using:

kubectl get prometheusrule task-api-alerts -n monitoring -o yaml

The live PrometheusRule contains:

TaskAPIHighHTTP5xxRate

The resource is located in the monitoring namespace.

The resource contains the Argo CD tracking annotation for:

monitoring:monitoring.coreos.com/PrometheusRule:monitoring/task-api-alerts

This confirms that the PrometheusRule is managed as part of the GitOps monitoring configuration.

## 5. Prometheus Rule Evidence

Screenshot:

docs/screenshots/phase-14/phase-14-01-prometheus-rule.png

This screenshot provides visual evidence of the Prometheus alerting rule.

## 6. PrometheusRule Configuration Evidence

Screenshot:

docs/screenshots/phase-14/phase-14-02a-prometheusrule-config.png

This screenshot provides visual evidence of the PrometheusRule configuration and alert definition.

## 7. Prometheus Rule Evaluation Evidence

Screenshot:

docs/screenshots/phase-14/phase-14-02b-prometheus-rule-evaluation.png

This screenshot provides visual evidence of Prometheus rule evaluation.

## 8. Alert State Evidence

Screenshot:

docs/screenshots/phase-14/phase-14-02c-prometheus-alert-state.png

This screenshot provides visual evidence of the current alert state after the controlled incident-response validation.

## 9. Controlled Incident Lifecycle

The high HTTP 5xx alert was previously validated through a controlled incident-response exercise.

The lifecycle included:

1. Healthy application state
2. Controlled HTTP 500 generation
3. HTTP 5xx metric increase
4. Prometheus detection
5. Alert pending state
6. Alert firing state
7. Alert visibility in the monitoring stack
8. Root-cause investigation
9. Corrective action
10. Kubernetes rollout
11. Application recovery
12. Prometheus metric recovery
13. Alert clearance
14. Final Kubernetes verification
15. Final Git verification

This provides operational evidence for the implemented high HTTP 5xx alert.

## 10. Alertmanager and Notification Flow

The monitoring stack includes Prometheus and Alertmanager.

The implemented alert contains:

- severity: warning
- service: task-api

The high HTTP 5xx alert was previously validated through the monitoring and incident-response workflow.

Alert detection and subsequent recovery were verified during the controlled incident exercise.

## 11. Application-Down Alert Verification

The project handbook describes an additional TaskApiDown application-down alert as part of the target Phase 14 design.

The actual repository and live Kubernetes configuration were inspected.

Repository search result:

TaskApiDown not found.

Live PrometheusRule alert names:

TaskAPIHighHTTP5xxRate

Therefore TaskApiDown is not currently implemented in the project's Git desired state or live Kubernetes state.

This evidence document does not claim that TaskApiDown was deployed or tested.

## 12. GitOps Consistency Verification

The Git repository contains:

TaskAPIHighHTTP5xxRate

The live Kubernetes PrometheusRule contains:

TaskAPIHighHTTP5xxRate

The repository and cluster therefore agree on the currently implemented alerting rule.

No manual Kubernetes alert modification was performed to introduce an alert that is absent from Git desired state.

## 13. Phase 14 Screenshots

The Phase 14 screenshot directory is:

docs/screenshots/phase-14/

The following four screenshots are present:

1. phase-14-01-prometheus-rule.png
2. phase-14-02a-prometheusrule-config.png
3. phase-14-02b-prometheus-rule-evaluation.png
4. phase-14-02c-prometheus-alert-state.png

Final screenshot count:

4

## 14. Evidence Limitations

The evidence accurately documents the alerting configuration that is currently implemented in the repository and deployed to Kubernetes.

The implemented alert is:

TaskAPIHighHTTP5xxRate

The evidence does not claim implementation or testing of TaskApiDown, because repository and live-cluster inspection confirmed that this alert is not currently present.

The previously completed incident-response evidence is used to document the operational lifecycle of the implemented high HTTP 5xx alert.

## 15. Final Result

Phase 14 successfully documents and verifies the implemented Prometheus alerting configuration for the Task API.

Final verified state:

- Git branch: main
- Git working tree: clean
- PrometheusRule: present
- Prometheus alert: TaskAPIHighHTTP5xxRate
- Threshold: greater than 5% HTTP 5xx
- Alert duration: 5 minutes
- Prometheus rule evaluation: verified
- Alert state: verified
- Git desired state: verified
- Live Kubernetes state: verified
- GitOps consistency: verified
- Phase 14 screenshots: 4
- Phase 14 screenshots committed and merged through PR #27

TaskApiDown remains a documented gap between the handbook's target alerting design and the alerting configuration currently implemented in the project.

No additional Kubernetes alert was manually created outside GitOps.
