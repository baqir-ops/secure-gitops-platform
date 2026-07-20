# Phase 10 — Argo CD and GitOps Verification

Captured: 2026-07-20T23:14:07+05:00

## Argo CD Applications
```text
NAME                        CLUSTER                         NAMESPACE    PROJECT        STATUS  HEALTH   SYNCPOLICY  CONDITIONS  REPO                                                     PATH    TARGET
argocd/metrics-server       https://kubernetes.default.svc  kube-system  default        Synced  Healthy  Auto-Prune  <none>      https://kubernetes-sigs.github.io/metrics-server/                3.13.1
argocd/secure-gitops-root   https://kubernetes.default.svc  argocd       default        Synced  Healthy  Auto-Prune  <none>      https://github.com/baqir-ops/secure-gitops-platform.git  argocd  main
argocd/task-api-dev         https://kubernetes.default.svc  dev          secure-gitops  Synced  Healthy  Auto-Prune  <none>      https://baqir-ops.github.io/secure-gitops-helm-chart             0.1.0
argocd/task-api-production  https://kubernetes.default.svc  production   secure-gitops  Synced  Healthy  Auto-Prune  <none>      https://baqir-ops.github.io/secure-gitops-helm-chart             0.1.0
argocd/task-api-staging     https://kubernetes.default.svc  staging      secure-gitops  Synced  Healthy  Auto-Prune  <none>      https://baqir-ops.github.io/secure-gitops-helm-chart             0.1.0
```

## Kubernetes Nodes
```text
NAME                                        STATUS   ROLES    AGE    VERSION               INTERNAL-IP   EXTERNAL-IP    OS-IMAGE                        KERNEL-VERSION                    CONTAINER-RUNTIME
ip-10-20-1-89.ap-south-1.compute.internal   Ready    <none>   111m   v1.35.6-eks-8f14419   10.20.1.89    13.207.57.70   Amazon Linux 2023.12.20260710   6.12.94-123.180.amzn2023.x86_64   containerd://2.2.4+unknown
```

## Application Deployments
```text
NAME       READY   UP-TO-DATE   AVAILABLE   AGE
task-api   1/1     1            1           21m
NAME       READY   UP-TO-DATE   AVAILABLE   AGE
task-api   1/1     1            1           21m
NAME       READY   UP-TO-DATE   AVAILABLE   AGE
task-api   2/2     2            2           21m
```

## Application Pods
```text
NAME                        READY   STATUS    RESTARTS   AGE
task-api-79fd78fc9d-vsxn8   1/1     Running   0          21m
NAME                       READY   STATUS    RESTARTS   AGE
task-api-78c66b69c-brt46   1/1     Running   0          21m
NAME                       READY   STATUS    RESTARTS   AGE
task-api-576db48fc-qc9cn   1/1     Running   0          21m
task-api-576db48fc-rbq6n   1/1     Running   0          21m
```

## Production HPA
```text
NAME       REFERENCE             TARGETS       MINPODS   MAXPODS   REPLICAS   AGE
task-api   Deployment/task-api   cpu: 2%/70%   2         5         2          21m

Conditions:
  Type            Status  Reason            Message
  ----            ------  ------            -------
  AbleToScale     True    ReadyForNewScale  recommended size matches current size
  ScalingActive   True    ValidMetricFound  the HPA was able to successfully calculate a replica count from cpu resource utilization (percentage of request)
  ScalingLimited  True    TooFewReplicas    the desired replica count is less than the minimum replica count
Events:
```

## Metrics
```text
NAME                                        CPU(cores)   CPU(%)   MEMORY(bytes)   MEMORY(%)
ip-10-20-1-89.ap-south-1.compute.internal   83m          4%       1389Mi          19%
NAME                       CPU(cores)   MEMORY(bytes)
task-api-576db48fc-qc9cn   2m           37Mi
task-api-576db48fc-rbq6n   2m           37Mi
```
