# Secure GitOps Platform Desired State

This repository is the source of truth for deployment intent and declarative
Argo CD resources for the Secure GitOps Task API.

## Deployment artifacts

- Helm repository: https://baqir-ops.github.io/secure-gitops-helm-chart
- Helm chart: `task-api`
- Chart version: `0.1.0`
- ECR repository: `950165721116.dkr.ecr.ap-south-1.amazonaws.com/secure-gitops-app`
- Initial immutable image: `sha-8b9c855fb43cf92be8bfafc201b4acd05e1ee2d8`

## Repository structure

```text
environments/
├── dev/values.yaml
├── staging/values.yaml
└── production/values.yaml

argocd/
├── project.yaml
└── applicationset.yaml

bootstrap/
platform/monitoring/
docs/screenshots/
```

## Promotion policy

The container image is built and scanned once. The same immutable `sha-*`
image is promoted without rebuilding it.

1. Development receives the verified image first.
2. Staging receives the exact dev image tag through a pull request.
3. Production receives the exact staging image tag through a reviewed pull request.
4. Rollback is performed with `git revert`, preserving Git as the source of truth.

The three environments currently use the same verified image as an initial
healthy baseline. Future changes must follow the promotion sequence above.

## Security controls

- No plaintext secrets are stored in this repository.
- Only immutable ECR `sha-*` image tags are permitted.
- The AppProject allow-lists approved source repositories and namespaces.
- Argo CD automatically prunes drift and self-heals managed resources.
- Ingress remains disabled initially to avoid unintended load-balancer charges.
- ServiceMonitor remains disabled until the Prometheus Operator CRD is installed.

## Deployment model

The ApplicationSet creates three Argo CD Applications from one template:

- `task-api-dev`
- `task-api-staging`
- `task-api-production`

The reusable Helm chart comes from the public chart repository. Environment
values come from this Git repository through Argo CD multi-source rendering.
