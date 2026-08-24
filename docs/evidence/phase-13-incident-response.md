# Phase 13 — Incident Response, Recovery & Alert Clearance Evidence

## 1. Phase Objective

Phase 13 validates the complete incident-response lifecycle for the `task-api` application running in the `dev` namespace.

This phase demonstrates:

- Controlled application failure
- HTTP 5xx generation
- Prometheus monitoring
- Alert detection
- Root-cause investigation
- Kubernetes configuration investigation
- Identification of a stale `FORCE_FAILURE=true` override
- Corrective action
- Kubernetes rollout
- Application recovery
- Prometheus metric recovery
- Alert clearance
- Final Kubernetes verification
- Final Git verification
- Screenshot evidence collection

---

## 2. Controlled Failure

A controlled failure was enabled for the `task-api` application in the `dev` namespace.

The application returned HTTP 500 from the health endpoint.

Observed response:

HTTP_STATUS=500

Response:

{"detail":"Simulated health failure"}

This confirmed that the application could intentionally generate an HTTP 5xx condition for incident-response testing.

---

## 3. Initial Dev Failure Verification

The initial configuration showed:

FORCE_FAILURE=true

The `task-api` Deployment was available and the application was running.

The health endpoint returned HTTP 500 as expected.

The application logs confirmed:

GET /health HTTP/1.1 500 Internal Server Error

This established the controlled failure condition.

---

## 4. Staging and Production Isolation

During the controlled development failure, staging and production were checked independently.

The purpose was to confirm that the incident was isolated to the `dev` environment.

The expected environment model was:

- Dev — controlled failure
- Staging — healthy
- Production — healthy

This demonstrates environment isolation within the GitOps platform.

---

## 5. Prometheus 5xx Monitoring

Prometheus was accessed through Kubernetes port-forwarding.

The Prometheus API responded successfully with:

HTTP_STATUS=200

The HTTP 5xx metric was queried for the `dev` namespace.

The monitoring system was therefore available to observe the application failure.

---

## 6. Alert Identification

The configured Prometheus alert is:

TaskAPIHighHTTP5xxRate

The alert is associated with:

- Namespace: dev
- Service: task-api
- Severity: warning

The alert is intended to detect an elevated HTTP 5xx rate.

The alert uses a five-minute rate window and a threshold of more than 5%.

---

## 7. Alert State During Incident

During the failure investigation, the alert was observed in Prometheus.

Observed alert information included:

state: pending

namespace: dev

service: task-api

severity: warning

value: 1e+00

This confirmed that Prometheus was detecting the failure condition.

---

## 8. CrashLoop Investigation

The initial failure caused the Kubernetes liveness probe to fail because the liveness endpoint was `/health`.

The application returned HTTP 500 from `/health`.

Kubernetes therefore reported:

Liveness probe failed: HTTP probe failed with statuscode: 500

The pod entered repeated restart behavior and eventually:

CrashLoopBackOff

The investigation showed that the application itself was not unexpectedly crashing. The liveness probe was intentionally causing Kubernetes to restart the container because the simulated health endpoint returned 500.

---

## 9. Root Cause Investigation

The ConfigMap was inspected.

The ConfigMap contained:

FORCE_FAILURE=false

However, the actual running container reported:

FORCE_FAILURE=true

This demonstrated that the ConfigMap value was not the effective value being used by the container.

The Deployment environment section was then inspected.

The Deployment contained an explicit environment variable:

name: FORCE_FAILURE

value: "true"

The Deployment also contained:

envFrom:
  configMapRef:
    name: task-api

Therefore, the explicit Deployment-level environment variable was overriding the ConfigMap value.

---

## 10. Root Cause

The root cause of the continued simulated failure was identified as a stale explicit Deployment environment variable:

FORCE_FAILURE=true

The ConfigMap correctly contained:

FORCE_FAILURE=false

but the Deployment explicitly supplied:

FORCE_FAILURE=true

The effective pod environment confirmed:

FORCE_FAILURE=true

Therefore:

Root Cause:
Stale explicit `FORCE_FAILURE=true` Deployment override.

Expected configuration:
`FORCE_FAILURE=false`

---

## 11. Corrective Action

The stale explicit `FORCE_FAILURE` environment variable was removed from the Deployment.

Before correction, the Deployment contained an explicit:

FORCE_FAILURE=true

After correction, the Deployment relied on:

envFrom:
  configMapRef:
    name: task-api

The ConfigMap remained the authoritative configuration source.

The ConfigMap value was:

FORCE_FAILURE=false

---

## 12. Kubernetes Recovery

After removing the stale environment variable, the Deployment was rolled out again.

The rollout completed successfully.

The final Deployment state was:

task-api   1/1   1   1

The new pod was:

task-api-f5f7c68cd-n7qz4

Final pod state:

READY: 1/1
STATUS: Running
RESTARTS: 0

The pod successfully recovered without restart loops.

---

## 13. Application and Alert Recovery

After the corrective action, the actual pod environment was verified:

FORCE_FAILURE=false

The application health endpoint was then tested.

Final response:

HTTP_STATUS=200

Response:

{"status":"healthy"}

The historical 5xx traffic was allowed to age out of the five-minute Prometheus window.

The final 5xx rate reached:

0

The final 5xx percentage reached:

0%

The Prometheus alert:

TaskAPIHighHTTP5xxRate

was no longer returned as active.

Final alert result:

ALERT CLEARED / NOT ACTIVE

This completed the incident-response lifecycle.

---

## 14. Final Independent Verification

The final independent Kubernetes verification showed:

Deployment:

task-api   1/1   1   1

Pod:

task-api-f5f7c68cd-n7qz4

READY: 1/1

STATUS: Running

RESTARTS: 0

Configuration:

FORCE_FAILURE=false

Application health:

HTTP_STATUS=200

Response:

{"status":"healthy"}

The final EKS node was:

ip-10-20-2-240.ap-south-1.compute.internal

Node status:

Ready

The current Git branch was:

main

The Git working tree was clean before the Phase 13 evidence files were added.

---

## 15. Phase 13 Evidence and Final Result

Six Phase 13 screenshots were captured and saved under:

docs/screenshots/phase-13/

The final screenshot set is:

1. phase-13-01-final-dev-health.png
2. phase-13-02-prometheus-alert-rule.png
3. phase-13-03-prometheus-5xx-rate.png
4. phase-13-04-alert-cleared-dev-recovery.png
5. phase-13-05-multi-environment-health.png
6. phase-13-06-git-evidence.png

Final verification:

| Item | Result |
|---|---|
| Controlled Dev failure | PASS |
| HTTP 500 generated | PASS |
| Prometheus monitoring | PASS |
| TaskAPIHighHTTP5xxRate detected | PASS |
| Root cause identified | PASS |
| Stale FORCE_FAILURE override identified | PASS |
| Override removed | PASS |
| Kubernetes rollout | PASS |
| Deployment 1/1 | PASS |
| Pod Running | PASS |
| Pod restarts after recovery | 0 |
| FORCE_FAILURE | false |
| Dev `/health` | HTTP 200 |
| Application response | healthy |
| 5xx rate | 0 |
| 5xx percentage | 0% |
| Alert cleared | PASS |
| Phase 13 screenshots | 6 |
| Git branch | main |

### Incident Lifecycle

Controlled Failure
→ HTTP 500
→ Prometheus Detection
→ TaskAPIHighHTTP5xxRate
→ Investigation
→ Stale FORCE_FAILURE Override Identified
→ Override Removed
→ Kubernetes Rollout
→ FORCE_FAILURE=false
→ HTTP 200
→ 5xx Rate = 0
→ Alert Cleared
→ Final Independent Verification

### Final Status

PHASE 13 COMPLETE

Incident-response workflow successfully demonstrated.

Application recovered successfully.

Prometheus alert successfully cleared.

Six screenshot evidence files captured.

Phase 13 evidence document created.

