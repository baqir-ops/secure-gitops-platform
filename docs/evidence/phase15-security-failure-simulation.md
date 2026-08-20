# Phase 15 — Security Failure Simulation Evidence

## 1. Objective

Validate the secure runtime configuration of the Task API and demonstrate controlled application failure behavior in the dev environment.

The existing FORCE_FAILURE configuration is used to intentionally make the /health endpoint return HTTP 500.

Expected behavior:

Git configuration
→ Argo CD synchronization
→ Task API failure
→ HTTP 500 health check
→ Kubernetes liveness probe failure
→ Container restart
→ CrashLoopBackOff

## 2. Repository

Repository:

secure-gitops-platform

Working directory:

~/secure-gitops-project/secure-gitops-platform

## 3. Git Branch

Phase 15 branch:

phase15/security-failure-simulations

Command used:

git branch --show-current

Expected result:

phase15/security-failure-simulations

## 4. Baseline Git Status

The Phase 15 branch started with a clean working tree.

Expected:

On branch phase15/security-failure-simulations

nothing to commit, working tree clean

## 5. Baseline Application Health

Before failure simulation, the Task API was healthy.

Command:

curl -i http://localhost:8080/

Observed:

HTTP/1.1 200 OK

Application response:

{"service":"secure-gitops-task-api","status":"running","version":"1.1.0"}

## 6. Health Endpoint

Before the failure simulation:

curl -i http://localhost:8080/health

Expected:

HTTP/1.1 200 OK

This confirms the application was initially healthy.

## 7. Readiness Endpoint

Before the failure simulation:

curl -i http://localhost:8080/ready

Expected:

HTTP/1.1 200 OK

The readiness endpoint continued to provide successful responses during the failure simulation.

## 8. Non-Root Runtime Identity

Command:

kubectl exec -n dev deployment/task-api -- id

Observed:

uid=10001(appuser) gid=10001(appgroup) groups=10001(appgroup)

The application runs as a non-root user.

UID:

10001

GID:

10001

## 9. Non-Root User Configuration

Deployment security context:

UID=10001
GID=10001
NonRoot=true

This prevents the application from running as root.

## 10. Privilege Escalation Protection

Command:

kubectl get deployment task-api -n dev \
-o jsonpath='{.spec.template.spec.containers[0].securityContext.allowPrivilegeEscalation}{"\n"}'

Observed:

false

Privilege escalation is disabled.

## 11. Linux Capabilities

Command:

kubectl get deployment task-api -n dev \
-o jsonpath='{.spec.template.spec.containers[0].securityContext.capabilities.drop}{"\n"}'

Observed:

["ALL"]

All Linux capabilities are dropped from the application container.

## 12. Read-Only Root Filesystem

Deployment configuration:

ReadOnlyRootFS=true

Write test:

kubectl exec -n dev deployment/task-api -- sh -c 'touch /app/security-test'

Observed:

touch: cannot touch '/app/security-test': Read-only file system

This confirms that the application cannot write to the container root filesystem.

## 13. Controlled Temporary Storage

The application has writable temporary storage.

Command:

kubectl exec -n dev deployment/task-api -- \
sh -c 'touch /tmp/security-test && ls -l /tmp/security-test && rm -f /tmp/security-test'

Observed:

-rw-r--r--. 1 appuser appgroup 0 /tmp/security-test

This demonstrates the intended security pattern:

Read-only root filesystem
+
Writable temporary directory

## 14. Service Account Token Protection

Command:

kubectl exec -n dev deployment/task-api -- \
sh -c 'if [ -f /var/run/secrets/kubernetes.io/serviceaccount/token ]; then echo "TOKEN EXISTS"; else echo "TOKEN NOT MOUNTED"; fi'

Observed:

TOKEN NOT MOUNTED

The Kubernetes service account token is not mounted into the application container.

## 15. Seccomp

Command:

kubectl get deployment task-api -n dev \
-o jsonpath='{.spec.template.spec.securityContext.seccompProfile.type}{"\n"}'

Observed:

RuntimeDefault

The workload uses the Kubernetes RuntimeDefault seccomp profile.

## 16. Complete Security Context

Observed configuration:

UID=10001
GID=10001
NonRoot=true
Seccomp=RuntimeDefault
ContainerUser=10001
ReadOnlyRootFS=true
PrivilegeEscalation=false
CapabilitiesDrop=["ALL"]

This demonstrates defense-in-depth runtime security.

## 17. Failure Simulation Configuration

The dev environment was configured with:

config:
  environment: dev
  forceFailure: "true"

The forceFailure value is rendered into the Kubernetes ConfigMap as:

FORCE_FAILURE: "true"

## 18. GitOps Deployment

The failure configuration was committed to Git and synchronized through Argo CD.

Argo CD application:

task-api-dev

The application initially showed:

SYNC STATUS: Synced
HEALTH STATUS: Healthy

During rollout of the failure configuration it entered:

SYNC STATUS: Synced
HEALTH STATUS: Progressing

## 19. Failure Pod

After synchronization, the Task API pod entered a failure state.

Observed:

task-api-ff97bbb57-qr4k8

0/1

CrashLoopBackOff

The pod repeatedly restarted because the liveness probe detected the intentional application failure.

## 20. Application Failure Logs

Command:

kubectl logs -n dev task-api-ff97bbb57-qr4k8 --previous

Observed:

GET /ready HTTP/1.1 200 OK

GET /health HTTP/1.1 500 Internal Server Error

The application intentionally returned HTTP 500 from /health.

## 21. Liveness Probe Failure

The deployment liveness probe targets:

/health

Because /health returned HTTP 500, Kubernetes considered the container unhealthy.

Pod events showed:

Liveness probe failed: HTTP probe failed with statuscode: 500

## 22. Kubernetes Restart Behavior

Pod events showed:

Container task-api failed liveness probe, will be restarted

The kubelet repeatedly terminated and restarted the container.

Observed restart count during the simulation reached hundreds of restarts.

This demonstrates automatic Kubernetes failure recovery behavior.

## 23. Complete Failure Chain

The complete Phase 15 failure simulation:

1. Git configuration changed.
2. forceFailure was enabled.
3. Argo CD synchronized the change.
4. Kubernetes created the updated pod.
5. Task API started successfully.
6. /ready continued returning HTTP 200.
7. /health returned HTTP 500.
8. Kubernetes liveness probe detected HTTP 500.
9. Kubelet terminated the container.
10. Container restarted.
11. The health check failed again.
12. Kubernetes entered CrashLoopBackOff behavior.

## 24. Security and Operational Validation

Phase 15 validated:

- Non-root execution
- UID/GID enforcement
- runAsNonRoot
- Read-only root filesystem
- Controlled writable /tmp storage
- allowPrivilegeEscalation=false
- Linux capabilities dropped
- RuntimeDefault seccomp
- Service account token not mounted
- Kubernetes readiness probe
- Kubernetes liveness probe
- Git-controlled failure simulation
- Argo CD synchronization
- Kubernetes automatic restart behavior
- CrashLoopBackOff detection
- Application health failure visibility

## Conclusion

Phase 15 successfully demonstrates secure runtime controls together with controlled failure testing.

The platform can intentionally introduce an application failure through GitOps and Kubernetes can detect that failure through the liveness probe and restart the unhealthy container.

The resulting operational chain is:

Git
→ Argo CD
→ Kubernetes Deployment
→ Task API
→ /health HTTP 500
→ Liveness Probe Failure
→ Kubelet Restart
→ CrashLoopBackOff

This provides evidence for both security hardening and failure-handling behavior in the Secure GitOps Platform.
