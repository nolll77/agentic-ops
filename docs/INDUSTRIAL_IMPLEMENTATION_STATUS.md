# Industrial implementation status

This document reports code that exists in this repository, not a claim that the
service is production-certified. A passing test covers its test scenarios only.
Cloud-provider, identity-provider, and operational guarantees require separate
deployment qualification.

For the concrete Entra tenant, image publication, single-replica deployment,
restore, and failure-exercise checklist, see
[`ENTRA_PREPRODUCTION_QUALIFICATION.md`](./ENTRA_PREPRODUCTION_QUALIFICATION.md).

## Status vocabulary

- **Implemented:** behavior exists in code.
- **CI-tested:** targeted automated tests exercise the behavior.
- **Preproduction / production:** requires a real deployment exercise and named
  operational approval; neither is implied by local tests.
- **Not implemented:** no production capability is claimed.

## Requirements-to-code mapping

### Run the alert worker

Run `uv run agentic-alert-worker` in a separate process using the same
`ALERT_OUTBOX_DB_PATH` as the API. Use `uv run agentic-alert-worker --once` to
process at most one queued alert. The worker performs deterministic diagnosis
through the core orchestrator and persists a simulated `investigate` episode
for explicitly mapped alerts. Unknown alerts remain `REVIEW_REQUIRED`; no
remediation is attempted.

The Helm chart can deploy the worker as a supervised sidecar sharing the API
pod's PVC. This profile is deliberately limited to one replica and one
single-writer pod using SQLite; it is persistent but not HA. Set a storage
class appropriate for the cluster. Set both API and worker to the same
`ALERT_OUTBOX_DB_PATH`, `POLICY_QUOTA_DB_PATH`, and `EVIDENCE_STORE_DIR`.
`COMPLETED` means the investigation episode was persisted, not that an
incident was remediated or service health recovered.

### Resume approved actions (simulation only)

`uv run agentic-approval-worker` consumes the durable approval execution
outbox. It rechecks the recorded quorum against the current
`SLACK_APPROVERS_JSON` role mapping before handing an action to the executor.
The worker refuses to start unless `SIMULATION_MODE=true`, and only marks a
request `SIMULATED` when the executor confirms that no external effect was
performed. If an approver no longer has the recorded role, the request stays
claimed and the outbox retries; it is not silently executed.

The Helm sidecar is opt-in (`approvalWorker.enabled=false` by default), needs
the API and worker to share the persistent approval/SCIM SQLite database. In
static-role mode it reads `SLACK_APPROVERS_JSON` from a projected Secret file
for each claim. With SCIM enabled, it reads the Entra-provisioned role directory
directly. The API's environment-based static role map still requires a pod
restart to affect new approvals. This enables durable queue resumption, not
orchestrator continuation or production execution.

### Microsoft Entra ID integration (code implemented, tenant qualification pending)

Set `ENTRA_TENANT_ID`, `ENTRA_API_AUDIENCE`, and `ENTRA_REQUIRED_ROLE` to allow
tenant-specific Entra access tokens on the protected admin routes. Once Entra
is configured, API-key authentication is disabled there too; machine callers
must use an Entra principal assigned the configured app role. Entra tokens must
be signed with RS256 and contain the configured issuer, audience,
tenant, validity period, and application `roles` claim. Assign the configured
app role (default `AgenticOps.Admin`) to the calling principal in the Entra
enterprise application.

Set `SCIM_ENABLED=true`, `SCIM_DB_PATH` (the API and approval worker must use
the same durable SQLite file), and a random `SCIM_BEARER_TOKEN` of at least 32
characters to enable `/scim/v2`. Configure Entra provisioning to send the
Slack member ID as each SCIM user's `externalId` and provision only groups
whose display names exactly match `SRE`, `SRE_LEAD`, `DATA_STEWARD`, or
`SECOPS`. SCIM updates to group membership and user `active` status take effect
on the next approval check; the approval worker independently rechecks current
membership before marking an action simulated. The chart keeps SCIM disabled
by default and injects its token from a Kubernetes Secret.

This is an implementation of the protocol path, not evidence that a particular
Entra tenant is configured correctly. Validate Entra provisioning mappings,
SCIM create/update/deactivate/delete behavior, app-role issuance, JWKS rotation
and provider/network outages in a dedicated preproduction tenant before using
it for operational approvals.

| Plan requirement | Current implementation | Verification / remaining qualification |
|---|---|---|
| Administrative route authentication | `AdminAPIKeyMiddleware` protects `/mcp`, `/api/diagnostics/*`, `/api/alerts/*`, and `/api/llm/probe`; supports current/previous API keys when Entra is unconfigured, or tenant-bound Entra JWTs when configured. Entra mode requires RS256 signature, issuer, audience, expiry, tenant and application-role checks and disables API-key bypass. CORS is disabled unless explicit origins are configured. | CI verifies signatures and rejects the wrong audience, tenant, role and expired tokens. Entra tenant/app registration, role assignment, key-service availability, conditional access, mTLS and production tenant validation still require deployment qualification. |
| Grafana webhook authentication | Dedicated current/previous shared secrets via `X-Grafana-Token` or Bearer token; missing configuration returns 503 and invalid credentials return 401. Existing body-size limit remains. | CI tests auth and malformed input. Grafana-native request signing, timestamp/replay validation and secret rotation in a deployed Grafana instance are not qualified. No forwarded client-IP header is trusted. |
| Durable alert acceptance | SQLite WAL outbox commits each accepted alert before HTTP 202; deterministic semantic fingerprints deduplicate repeated events; tracking IDs and a protected status endpoint are provided. | CI tests persistence, duplicate delivery, lease recovery, retry and terminal failure. This is local/single-node durability; multi-node HA, backups and restore remain unqualified. |
| Alert investigation worker | `agentic-alert-worker` consumes the outbox, applies an exact-name versioned mapping, uses the core orchestrator with deterministic alert evidence and a non-mutating `investigate` action, then stores the episode ID. Unknown/malformed names become `REVIEW_REQUIRED`; the status endpoint exposes the mapping version, risk ID, and episode ID. | CI covers end-to-end episode persistence and recovery if the worker crashes after the episode is saved. The Helm sidecar/PVC is a single-replica SQLite profile, not HA. Diagnosis is deterministic from the alert payload; no LLM or external remediation is invoked. |
| Deterministic policy quota | `AtomicQuotaManager` performs sliding-window reservations in a SQLite `BEGIN IMMEDIATE` transaction; `PolicyEngine` uses it when evaluating configured rate-limited actions. | Concurrent test now passes without `xfail`; persistent storage is shared only by processes using the same database file. A multi-host profile needs a qualified shared transactional adapter. |
| Target inventory boundary | Orchestrated policy decisions deny with `INV-001` when no inventory provider is injected; scenario tests use an explicit bounded fixture inventory. | No production inventory adapter or authoritative `inventory.yaml` loader is configured. Action target patterns are format checks, not an allowlist; real target allowlisting remains a deployment gate. |
| Approval identity and separation of duties | Approval proposals require a requester ID, are immutable by digest, reject requester self-approval, require configured groups, and reject invalid decisions. Optional Entra SCIM 2.0 provisioning maps `externalId` to Slack member ID and role-group membership to approver roles; inactive or deprovisioned users lose authorization. Static `SLACK_APPROVERS_JSON` remains available only when SCIM is disabled. | CI covers SCIM user/group provisioning, Slack ID mapping, membership revocation, OIDC token claims, quorum and the approval worker's recheck before simulation. Entra enterprise-app mappings, provisioning credentials, scope, tenant policy, monitoring and production deprovisioning latency still require qualification. |
| Safe approval handoff | When quorum is reached, the same SQLite transaction marks the request claimed and inserts a durable execution-outbox record. `agentic-approval-worker` claims it with expiring leases, rechecks current static roles or SCIM-provisioned Entra membership, and invokes the executor only in simulation mode. Successful simulated results are persisted as `SIMULATED`; failures retry and eventually become terminal. | CI covers durable claims, role revalidation/revocation, worker recovery state, and refusal of live mode. This resumes the queued action through the executor; it does not continue a suspended orchestrator episode. Entra tenant provisioning and production execution remain unqualified. |
| Live execution protection | Simulation is default. The gateway requires explicit live opt-in, acknowledgement, a named profile, exact action/target allowlists and a readable kill-switch directory; its qualified-action set is deliberately empty. | CI tests default denial, no qualified action, and active kill-switch denial. Environment flags alone cannot enable live use. The kill-switch is an application gateway check, not an independent infrastructure control until separately deployed and exercised. |
| Cryptographic evidence | Existing HMAC/hash-chain and Merkle functionality remains. | Ed25519 epoch manifests, KMS/HSM key lifecycle, TSA, public transparency log/witnesses and managed WORM storage are not implemented or qualified here. `chmod 0444` is not WORM. |
| Post-action verification and compensation | Existing executors contain limited action-specific verification; no general action contract exists. | A complete action-by-action verification/compensation catalog, external execution gateway for every adapter, and rollback GameDays remain required. |
| Cloud portability | The new outbox and quota code use SQLite and framework-independent interfaces for worker handlers. | No cloud adapter or deployment profile is qualified. SQLite is not a multi-region or multi-node HA claim. Each identity, database/queue, key, storage, execution and telemetry adapter must pass contract tests on the target platform. |
| SRE operation | No quantified production SLO/RPO/RTO is asserted by this implementation. | Dashboards, paging, backup/restore exercises, runbooks, GameDays, named service ownership, deployment rollback and promotion reviews remain to be delivered. |

## Safety invariants exercised in CI

1. Unknown or unauthorized administrative calls are rejected; missing auth
   configuration fails closed.
2. Grafana events are not acknowledged until persisted, and repeated semantic
   events map to the same tracking record.
3. Expired worker leases can be reclaimed; a stale worker cannot complete a
   lease owned by another worker.
4. Approval requests require a requester; self-approval, unauthorized roles and
   changed proposals cannot satisfy quorum.
5. Concurrent quota reservations cannot exceed the configured limit when they
   share the same SQLite database.
6. Live execution is refused unless explicit configuration is complete, and an
   active kill-switch blocks it.

These are bounded test claims, not universal formal proofs. In particular,
exactly-once external effects cannot be guaranteed unless the target API
supports idempotency or a reliable reconciliation protocol.

## Deployment promotion gates still required

Before **observation/simulation** can be called production-capable, deploy and
operate the API and `agentic-alert-worker` beside a persistent outbox on a
qualified single-node or shared-store profile, exercise durable episode
investigation, and verify that no path can mutate a real target. The current
alert worker persists a simulated investigation episode; `COMPLETED` means
its outbox delivery finished, not that the incident was resolved. The Helm
container port and probes use the Docker image's configured port 8001.

Before **assisted preproduction**, configure and qualify the Entra app and
SCIM provisioning using
[`ENTRA_PREPRODUCTION_QUALIFICATION.md`](./ENTRA_PREPRODUCTION_QUALIFICATION.md),
connect resumed approvals to the orchestrator's persisted episode state with
restart-safe idempotency, use isolated targets, and exercise crash recovery,
quota contention, key/secret rotation, backups and restoration. The current
approval worker only simulates supported executor actions; it does not resume
a suspended orchestrator episode.

Before **bounded autonomy**, qualify each action and target individually,
deploy an independent execution kill-switch, test target idempotency or
reconciliation, validate compensation, and obtain named SRE/security approval
against measured SLOs. Promotion on one cloud does not qualify another.
