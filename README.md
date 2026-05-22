# nomos-demo

Demo repo showing how to block GitHub PRs that violate platform governance rules using [Nomos](https://github.com/constitutional-governance/nomos).

## How it works

Every PR that changes files under `resources/` triggers a GitHub Actions workflow that validates each resource against the Nomos governance server. If any resource fails validation, the check fails and the PR cannot be merged.

```
PR opened
    ↓
GitHub Actions reads resources/*.yaml
    ↓
Calls Nomos REST API for each topic, SA, and RBAC binding
    ↓
❌ Any failure → check fails → merge blocked
✅ All pass    → check passes → merge allowed
```

## Resources

Add your platform resources to `resources/`:

- `topics.yaml` — Kafka topic names
- `service-accounts.yaml` — Kafka service account names
- `rbac.yaml` — RBAC role bindings

## Setup

Point the workflow at your own Nomos server by setting `NOMOS_SERVER` in the workflow env, or as a repository secret.

See [Nomos](https://github.com/constitutional-governance/nomos) for server setup and [nomos-template](https://github.com/constitutional-governance/nomos-template) for governance repo structure.
