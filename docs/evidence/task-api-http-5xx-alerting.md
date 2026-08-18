# Task API HTTP 5xx Alerting Evidence

## Objective

Implement and verify HTTP 5xx error-rate alerting for the Task API using
Prometheus, PrometheusRule, ServiceMonitor, Argo CD, and Alertmanager.

The objective was to verify the complete alert lifecycle:

1. Deploy the alert through GitOps.
2. Confirm Task API metrics are available.
3. Generate a controlled HTTP 500 failure.
4. Confirm Prometheus detects the elevated 5xx rate.
5. Confirm the alert enters `pending`.
6. Confirm the alert enters `firing` after 5 minutes.
7. Confirm Alertmanager receives the alert.
8. Remove the controlled failure.
9. Confirm the alert condition clears.
10. Remove temporary test resources.
11. Confirm the normal Task API remains healthy.

---

## 1. PrometheusRule

The alert is defined in:

```text
platform/monitoring/manifests/task-api-alerts.yaml
```

Resource:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: task-api-alerts
  namespace: monitoring
```

Alert name:

```text
TaskAPIHighHTTP5xxRate
```

PromQL expression:

```promql
(
  sum by (namespace) (
    rate(app_http_requests_total{status=~"5.."}[5m])
  )
  /
  sum by (namespace) (
    rate(app_http_requests_total[5m])
  )
) > 0.05
```

Alert configuration:

```yaml
for: 5m

labels:
  severity: warning
  service: task-api
```

The alert therefore fires when the HTTP 5xx response rate exceeds
5% for five continuous minutes.

---

## 2. GitOps Deployment

The PrometheusRule was added through a feature branch and Pull Request.

Pull Request:

```text
#17 - Add Task API HTTP error rate alert
```

The GitHub Actions validation check completed successfully:

```text
GitOps Validation/Validate...
✓ successful
```

The Pull Request was squash-merged into `main`.

The resulting commit was:

```text
2ef1392 Add Task API HTTP error rate alert (#17)
```

Argo CD subsequently synchronized the monitoring Application.

---

## 3. Argo CD Monitoring Application

The monitoring Application uses:

```text
kube-prometheus-stack
```

and the Git repository contains:

```text
platform/monitoring/manifests/task-api-alerts.yaml
```

The monitoring Application uses automated synchronization with:

```yaml
prune: true
selfHeal: true
```

The monitoring Application was verified as:

```text
monitoring   Synced   Healthy
```

---

## 4. PrometheusRule Verification

The deployed PrometheusRule was verified with:

```bash
kubectl get prometheusrule -n monitoring task-api-alerts
```

Result:

```text
NAME              AGE
task-api-alerts   43h
```

This confirms that the PrometheusRule exists in the monitoring namespace.

---

## 5. Task API Metrics

The Task API exposes a Prometheus metrics endpoint:

```text
/metrics
```

The application defines the following counter:

```text
app_http_requests_total
```

The metric contains the following labels:

```text
method
path
status
```

The application middleware records the HTTP response status for each
request.

Example normal metrics:

```text
app_http_requests_total{method="GET",path="/ready",status="200"}
app_http_requests_total{method="GET",path="/health",status="200"}
```

The application also exposes:

```text
app_http_request_duration_seconds
```

for HTTP request latency measurements.

---

## 6. ServiceMonitor

The Task API has a ServiceMonitor in the `dev` namespace.

The ServiceMonitor configuration was verified with:

```bash
kubectl get servicemonitor task-api -n dev -o yaml
```

The endpoint configuration is:

```yaml
endpoints:
  - interval: 30s
    path: /metrics
    port: http
    scrapeTimeout: 10s
```

The ServiceMonitor uses:

```yaml
labels:
  release: monitoring
```

The selector targets the Task API:

```yaml
selector:
  matchLabels:
    app.kubernetes.io/instance: task-api
    app.kubernetes.io/name: task-api
```

Prometheus successfully discovered and scraped the Task API metrics.

---

## 7. Controlled Failure Mechanism

The Task API supports a controlled failure mechanism through:

```text
FORCE_FAILURE=true
```

The application code checks this environment variable in the `/health`
endpoint.

When enabled, the application returns:

```text
HTTP 500 Internal Server Error
```

with:

```json
{
  "detail": "Simulated health failure"
}
```

The relevant application behavior is:

```python
if os.getenv("FORCE_FAILURE", "false").lower() == "true":
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Simulated health failure",
    )
```

This mechanism was used only for controlled alert testing.

---

## 8. HTTP 500 Generation

During the controlled failure test, the test Task API instance had:

```text
FORCE_FAILURE=true
```

The endpoint was verified with:

```bash
curl -i http://localhost:8081/health
```

Result:

```text
HTTP/1.1 500 Internal Server Error
```

Response:

```json
{"detail":"Simulated health failure"}
```

The application metrics subsequently contained:

```text
app_http_requests_total{method="GET",path="/health",status="500"}
```

This confirmed that the application was correctly exposing the simulated
HTTP 500 response as a Prometheus metric.

---

## 9. Prometheus Metric Verification

Prometheus was queried directly for HTTP 500 metrics:

```bash
curl -sG http://localhost:9090/api/v1/query \
  --data-urlencode 'query=app_http_requests_total{status="500"}'
```

The result included the Task API metric with:

```text
namespace: dev
path: /health
status: 500
service: task-api
```

This confirmed that Prometheus was receiving the application's HTTP 500
metric.

---

## 10. 5xx Rate Calculation

The alert expression was tested directly in Prometheus:

```promql
sum by (namespace) (
  rate(app_http_requests_total{status=~"5.."}[5m])
)
/
sum by (namespace) (
  rate(app_http_requests_total[5m])
)
```

During the controlled failure test, the calculated value exceeded the
configured threshold:

```text
0.05
```

Examples observed during the test included values such as:

```text
0.5597548938306369
0.8225882511336241
0.8894348894348894
```

These values correspond to approximately:

```text
55.9%
82.3%
88.9%
```

and therefore exceeded the configured 5% threshold.

---

## 11. Prometheus Alert State: Pending

After the 5xx rate exceeded the threshold, the alert initially entered:

```text
pending
```

The alert was observed with:

```text
alertname: TaskAPIHighHTTP5xxRate
namespace: dev
service: task-api
severity: warning
```

The alert had:

```text
for: 5m
```

configured.

This confirmed that Prometheus correctly respected the five-minute
pending period before firing the alert.

---

## 12. Prometheus Alert State: Firing

After the five-minute duration elapsed, the alert transitioned to:

```text
firing
```

Observed alert information:

```text
alertname: TaskAPIHighHTTP5xxRate
namespace: dev
service: task-api
severity: warning
```

An observed firing value was approximately:

```text
0.889
```

which represented an HTTP 5xx rate significantly above the 5% threshold.

This confirmed the Prometheus alert evaluation and firing behavior.

---

## 13. Alertmanager Verification

Alertmanager was queried through:

```text
/api/v2/alerts
```

The Task API alert was successfully received by Alertmanager.

Observed information:

```text
ALERT: TaskAPIHighHTTP5xxRate
STATUS: active
NAMESPACE: dev
SERVICE: task-api
SEVERITY: warning
```

The Alertmanager response also contained:

```text
alertname: TaskAPIHighHTTP5xxRate
namespace: dev
service: task-api
severity: warning
```

The alert was therefore successfully propagated through:

```text
Application
    ↓
Prometheus metrics
    ↓
ServiceMonitor
    ↓
Prometheus
    ↓
PrometheusRule
    ↓
Alertmanager
```

---

## 14. Alert Resolution

After the alert had successfully fired, the controlled failure test
was stopped.

The temporary test resources were removed.

The real development environment was restored to:

```yaml
config:
  environment: dev
  forceFailure: "false"
```

The real Task API deployment was verified as healthy.

Prometheus was then queried again using:

```promql
sum by (namespace) (
  rate(app_http_requests_total{status=~"5.."}[5m])
)
/
sum by (namespace) (
  rate(app_http_requests_total[5m])
)
```

The final query returned:

```json
{
    "status": "success",
    "data": {
        "resultType": "vector",
        "result": []
    }
}
```

This confirmed that there was no longer a current namespace with a
measurable HTTP 5xx rate matching the query.

The Prometheus active-alert query:

```bash
curl -s http://localhost:9090/api/v1/alerts \
  | python3 -m json.tool \
  | grep -A30 "TaskAPIHighHTTP5xxRate"
```

no longer returned the Task API alert.

Therefore the alert condition had cleared.

---

## 15. Temporary Test Resource Cleanup

The controlled failure test used a temporary Pod:

```text
task-api-alert-test
```

and a temporary Service:

```text
task-api-alert-test
```

The temporary Pod was deleted:

```bash
kubectl delete pod task-api-alert-test -n dev
```

Result:

```text
pod "task-api-alert-test" deleted from dev namespace
```

The temporary Service was deleted:

```bash
kubectl delete svc task-api-alert-test -n dev
```

Result:

```text
service "task-api-alert-test" deleted from dev namespace
```

The temporary test resources were therefore completely removed.

---

## 16. Final Task API Configuration

The real development ConfigMap was verified with:

```bash
kubectl get configmap task-api -n dev -o yaml | grep FORCE_FAILURE
```

Result:

```text
FORCE_FAILURE: "false"
```

The real Task API therefore remained configured for normal operation.

---

## 17. Final Argo CD Verification

The final Argo CD state was:

```text
NAME                  SYNC STATUS   HEALTH STATUS
metrics-server        Synced        Healthy
monitoring            Synced        Healthy
secure-gitops-root    Synced        Healthy
task-api-dev          Synced        Healthy
task-api-production   Synced        Healthy
task-api-staging      Synced        Healthy
```

All applications were:

```text
Synced
Healthy
```

This confirms that the GitOps platform remained in a healthy state after
the alert test and cleanup.

---

## 18. Final Dev Pod Verification

The development namespace was verified with:

```bash
kubectl get pods -n dev
```

Result:

```text
NAME                       READY   STATUS    RESTARTS   AGE
task-api-f5f7c68cd-5fx8m   1/1     Running   0          40h
```

The real Task API was therefore:

```text
1/1 Running
```

with no container restarts reported in the final verification.

---

## 19. Final Prometheus Readiness

Prometheus was verified using:

```bash
curl -s http://localhost:9090/-/ready
```

Result:

```text
Prometheus Server is Ready.
```

This confirms that Prometheus remained operational after the alert test.

---

## 20. Git State

The final repository state was verified with:

```bash
git status
```

Result:

```text
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

The relevant Git history was:

```text
fc56d80 Restore Task API dev health (#19)
0961357 Enable controlled Task API failure in dev (#18)
2ef1392 Add Task API HTTP error rate alert (#17)
866f692 Allow task-api namespaces in AppProject (#16)
fa41969 Enable ServiceMonitor validation for all environments (#15)
```

---

## 21. End-to-End Result

The HTTP 5xx alerting workflow was successfully verified end-to-end.

The complete lifecycle was demonstrated:

```text
Normal Task API
      ↓
Controlled failure enabled
      ↓
HTTP 500 generated
      ↓
app_http_requests_total{status="500"}
      ↓
ServiceMonitor scraped metrics
      ↓
Prometheus received metrics
      ↓
5xx rate exceeded 5%
      ↓
Prometheus alert PENDING
      ↓
5 minutes elapsed
      ↓
Prometheus alert FIRING
      ↓
Alertmanager received alert
      ↓
Alertmanager status ACTIVE
      ↓
Controlled failure removed
      ↓
Temporary test resources deleted
      ↓
5xx rate returned to normal
      ↓
Prometheus alert resolved
      ↓
Real Task API healthy
      ↓
Argo CD Synced / Healthy
```

---

## 22. Verification Checklist

| Test | Result |
|---|---|
| PrometheusRule deployed through Argo CD | ✅ |
| PrometheusRule exists | ✅ |
| ServiceMonitor configured | ✅ |
| Task API metrics exposed | ✅ |
| Prometheus discovers Task API metrics | ✅ |
| Controlled HTTP 500 generated | ✅ |
| HTTP 500 metric observed | ✅ |
| 5xx PromQL calculation verified | ✅ |
| 5% threshold exceeded | ✅ |
| `for: 5m` verified | ✅ |
| Prometheus alert entered pending | ✅ |
| Prometheus alert entered firing | ✅ |
| Alertmanager received alert | ✅ |
| Alertmanager status became active | ✅ |
| Controlled failure removed | ✅ |
| Alert condition cleared | ✅ |
| Temporary Pod removed | ✅ |
| Temporary Service removed | ✅ |
| `FORCE_FAILURE=false` restored | ✅ |
| Task API healthy | ✅ |
| Argo CD applications Synced/Healthy | ✅ |
| Prometheus ready | ✅ |
| Git working tree clean | ✅ |

---

## Conclusion

The Task API HTTP 5xx alerting implementation successfully demonstrated
a production-style observability workflow using Kubernetes, Prometheus,
PrometheusRule, ServiceMonitor, Alertmanager, and Argo CD.

The test verified both sides of the alert lifecycle:

**Detection**

```text
HTTP 500 → metrics → Prometheus → pending → firing → Alertmanager
```

and **Recovery**

```text
failure removed → 5xx rate clears → alert resolves → cleanup → healthy
```

The development environment was restored to its normal GitOps-managed
state after testing.
