# Phase 10 — Git-Based Image Promotion

Captured: 2026-07-21T00:24:37+05:00

## Objective

Publish a new immutable application image and promote it only to the development environment through Git and Argo CD.

## Application Release

```text
Version: 1.1.0
Application commit: ff08b9c42533e1611d91882d75bc3fbf01d7fd67
Image tag: sha-ff08b9c42533e1611d91882d75bc3fbf01d7fd67
Image digest: sha256:359ad21e90244d013afa79e8e037eecd4771795e9dd2ed6f0142222a7e1e30d9
GitHub Actions run: 29770482229
```

## Argo CD Application

```text
NAME           SYNC     HEALTH    REVISION
task-api-dev   Synced   Healthy   <none>
```

## Environment Images

```text
dev: 950165721116.dkr.ecr.ap-south-1.amazonaws.com/secure-gitops-app:sha-ff08b9c42533e1611d91882d75bc3fbf01d7fd67
staging: 950165721116.dkr.ecr.ap-south-1.amazonaws.com/secure-gitops-app:sha-8b9c855fb43cf92be8bfafc201b4acd05e1ee2d8
production: 950165721116.dkr.ecr.ap-south-1.amazonaws.com/secure-gitops-app:sha-8b9c855fb43cf92be8bfafc201b4acd05e1ee2d8
```

## Development Rollout

```text
deployment "task-api" successfully rolled out
NAME       READY   UP-TO-DATE   AVAILABLE   AGE
task-api   1/1     1            1           92m
```

## Live API Verification

```json
{
  "service": "secure-gitops-task-api",
  "status": "running",
  "version": "1.1.0"
}
```

## Result

- CI tests and security scans passed.
- GitHub OIDC published a new immutable image to Amazon ECR.
- Only the development values file was updated.
- Argo CD automatically deployed the new image.
- Staging and production remained on the previous immutable image.
- The live development API returned version 1.1.0.
