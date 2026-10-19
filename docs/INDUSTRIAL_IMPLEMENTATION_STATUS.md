# Industrial implementation status

For the detailed repository-to-production mapping, configuration keys,
operational ownership, and promotion gates, see
[`INDUSTRIAL_PRODUCTION_BLUEPRINT.md`](./INDUSTRIAL_PRODUCTION_BLUEPRINT.md).

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
The chart requires `crypto.signingSecretName` to refer to a pre-created
Kubernetes Secret containing a persistent `LEDGER_SECRET_KEY`; it injects that
same key into the API and workers. With Entra disabled, `apiAuth.secretName`
must reference a Secret containing `ADMIN_API_KEY`. While the alert worker is
enabled, `grafanaWebhook.secretName` must reference a Secret containing
`GRAFANA_WEBHOOK_SECRET`. Current and previous keys may be rotated using the
optional `previousSecretKey` values. Do not use a newly generated per-process
key for a persistent ledger.
`COMPLETED` means the investigation episode was persisted, not that an
incident was remediated or service health recovered.

### Resume approved actions (simulation only)

`uv run agentic-approval-worker` consumes the durable approval execution
outbox. The alert orchestrator first persists the suspended episode and then
opens an idempotent frozen proposal in the shared `APPROVAL_DB_PATH`, using
`APPROVAL_REQUESTER_ID` (default `agentic-ops-alert-worker`). It rechecks the recorded quorum against the current
`SLACK_APPROVERS_JSON` role mapping before handing an action to the executor.
The worker refuses to start unless `SIMULATION_MODE=true`, and only marks a
request `SIMULATED` when the executor confirms that no external effect was
performed. If an approver no longer has the recorded role, the request stays
claimed and the outbox retries; it is not silently executed.

The Helm sidecar is opt-in (`approvalWorker.enabled=false` by default), needs
the API, alert worker, and approval worker to share the persistent
approval/SCIM SQLite database and evidence directory. In
static-role mode it reads `SLACK_APPROVERS_JSON` from a projected Secret file
for each claim. With SCIM enabled, it reads the Entra-provisioned role directory
directly. The API's environment-based static role map still requires a pod
restart to affect new approvals. After simulation, the worker appends
`EXECUTING → RESOLVED` and the approval evidence to the original episode's
signed ledger. A retry after evidence append but before outbox acknowledgment
does not repeat the simulation. Live execution remains disabled; Slack
notification delivery, denial reconciliation and deployment-level recovery
are not yet qualified.

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
| Durable alert acceptance | SQLite WAL outbox commits each accepted alert before HTTP 202; deterministic semantic fingerprints deduplicate repeated events; tracking IDs and a protected status endpoint are provided. | CI tests persistence, duplicate delivery, lease recovery, retry and terminal failure, including crashes after claim and after a handler effect but before acknowledgment. Delivery is at least once; external handlers need `tracking_id` idempotency or reconciliation. This remains local/single-node durability, not HA. |
| Alert investigation worker | `agentic-alert-worker` consumes the outbox, applies an exact-name versioned mapping, uses the core orchestrator with deterministic alert evidence and a non-mutating `investigate` action, then stores the episode ID. Unknown/malformed names become `REVIEW_REQUIRED`; the status endpoint exposes the mapping version, risk ID, and episode ID. | CI covers idempotent episode persistence and lease recovery after abrupt process exit. The alert worker also opens a durable approval request when policy suspends an episode. Both API and worker use a configured exact-name inventory; missing, modified, or stale inventory denies policy decisions. The Helm sidecar/PVC is single-replica SQLite, not HA. Diagnosis is deterministic; no LLM or external remediation is invoked. |
| Deterministic policy quota | `AtomicQuotaManager` performs sliding-window reservations in a SQLite `BEGIN IMMEDIATE` transaction; `PolicyEngine` uses it when evaluating configured rate-limited actions. | Concurrent test now passes without `xfail`; persistent storage is shared only by processes using the same database file. A multi-host profile needs a qualified shared transactional adapter. |
| Target inventory boundary | A local YAML inventory adapter is available through `AGENTIC_OPS_INVENTORY_PATH`; chart users may mount an exact-name ConfigMap inventory in read-only mode. Missing, stale, malformed, modified, or unknown inventory/targets fail closed; user-supplied MCP replica/criticality hints cannot act as inventory. The inventory content hash is recorded in policy verdicts and episodes. | CI covers expiry during process lifetime and file replacement: modification invalidates the loaded inventory immediately, and restart/reload is required to adopt the new version. Inventory is operator-maintained, not synchronized with an authoritative platform source; target ownership and drift detection remain operational responsibilities. |
| Approval identity and separation of duties | Approval proposals require a requester ID, are immutable by digest, reject requester self-approval, require configured groups, and reject invalid decisions. Optional Entra SCIM 2.0 provisioning maps `externalId` to Slack member ID and role-group membership to approver roles; inactive or deprovisioned users lose authorization. Static `SLACK_APPROVERS_JSON` remains available only when SCIM is disabled. | CI covers SCIM user/group provisioning, Slack ID mapping, membership revocation, OIDC token claims, quorum and the approval worker's recheck before simulation. Entra enterprise-app mappings, provisioning credentials, scope, tenant policy, monitoring and production deprovisioning latency still require qualification. |
| Safe approval handoff | When policy requires approval, the orchestrator persists a frozen proposal in `ApprovalRepo` after saving the suspended episode. On quorum, one SQLite transaction marks it claimed and inserts a durable execution-outbox record. `agentic-approval-worker` rechecks current static roles or SCIM membership, simulates the action only, then appends `EXECUTING → RESOLVED` and the result to the original episode's signed evidence chain. Retry after evidence append is idempotent. The alert worker shares the persistent approval database and uses `APPROVAL_REQUESTER_ID` (default `agentic-ops-alert-worker`). | CI covers request creation, digest binding, quorum, role revalidation/revocation, resumed episode evidence, recovery after append-before-ack, and refusal of live mode. The same-episode software path is implemented; Slack delivery, denial-ledger reconciliation, tenant provisioning, real deployment recovery and production execution remain unqualified. |
| Live execution protection | Simulation is default. The gateway requires explicit live opt-in, acknowledgement, a named profile, exact action/target allowlists and a readable kill-switch directory; its qualified-action set is deliberately empty. | CI tests default denial, no qualified action, and active kill-switch denial. Environment flags alone cannot enable live use. The kill-switch is an application gateway check, not an independent infrastructure control until separately deployed and exercised. |
| Cryptographic evidence | Existing HMAC/hash-chain and Merkle functionality remains. | Ed25519 epoch manifests, KMS/HSM key lifecycle, TSA, public transparency log/witnesses and managed WORM storage are not implemented or qualified here. `chmod 0444` is not WORM. |
| Post-action verification and compensation | Existing executors contain limited action-specific verification; no general action contract exists. | A complete action-by-action verification/compensation catalog, external execution gateway for every adapter, and rollback GameDays remain required. |
| Cloud portability | The new outbox and quota code use SQLite and framework-independent interfaces for worker handlers. | No cloud adapter or deployment profile is qualified. SQLite is not a multi-region or multi-node HA claim. Each identity, database/queue, key, storage, execution and telemetry adapter must pass contract tests on the target platform. |
| SRE operation | `agentic-ops-db backup-set` creates a manifest of SQLite snapshots and the signed evidence directory; `verify-set` checks file hashes, database integrity and ledger chain; `restore-set` verifies and restores to a new isolated path. CI runs a multi-database restore drill. `agentic-ops-benchmark-alerts --sizes 100,500,1000` measures a local load matrix and optional throughput/p95 thresholds. No production SLO/RPO/RTO is asserted. | Copy and restore from the selected off-host backup, establish actual RPO/RTO, load/failure tests on the target machine, dashboards, paging, GameDays, ownership, rollback and promotion reviews remain to be exercised or delivered. Quiesce writers: the tool does not create a cross-database transaction boundary. |

## Safety invariants exercised in CI

1. Unknown or unauthorized administrative calls are rejected; missing auth
   configuration fails closed.
2. Grafana events are not acknowledged until persisted, and repeated semantic
   events map to the same tracking record.
3. Expired worker leases can be reclaimed; a stale worker cannot complete a
   lease owned by another worker.
4. Approval requests require a requester; self-approval, unauthorized roles and
   changed proposals cannot satisfy quorum. A completed simulation appends the
   outcome to the original pending episode rather than creating a new episode.
5. Concurrent quota reservations cannot exceed the configured limit when they
   share the same SQLite database.
6. Live execution is refused unless explicit configuration is complete, and an
   active kill-switch blocks it.

These are bounded test claims, not universal formal proofs. In particular,
exactly-once external effects cannot be guaranteed unless the target API
supports idempotency or a reliable reconciliation protocol.

## Local exercises added in v0.1.6

- The backup-set drill includes named SQLite databases and the signed evidence
  directory, then verifies the manifest hashes, SQLite integrity and evidence
  chain before restoring into a new isolated directory. The operator must
  quiesce all writers; consistency is per database, not an atomic transaction
  across files. A test restore in CI does not qualify an off-host backup target.
- Worker resilience tests cover idle-before-claim, active-lease recovery,
  handler failure/retry and a crash after a simulated effect but before queue
  acknowledgment. Delivery is at least once and makes no exactly-once claim
  for external effects.
- Approval continuation tests cover creation of the frozen request from a
  persisted pending episode, quorum, simulation-only processing and idempotent
  recovery after evidence append. The result is appended to the original
  episode ID. Live execution, denial reconciliation, real Slack delivery and
  deployment recovery remain outside this qualification.
- Inventory tests cover expiry while a process is running and replacement of
  the inventory file. Changed/invalid content fails closed; the process must
  restart or reload to accept a new inventory version.
- The local load matrix reports observations for each requested queue size.
  Optional thresholds are operator-selected local checks, not service SLOs.

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
validate the request-to-episode approval path in the deployed profile, use
isolated targets, and exercise crash recovery, quota contention, key/secret
rotation, off-host backups and restoration. The approval continuation is
implemented in simulation only; live actions remain disabled.

Before **bounded autonomy**, qualify each action and target individually,
deploy an independent execution kill-switch, test target idempotency or
reconciliation, validate compensation, and obtain named SRE/security approval
against measured SLOs. Promotion on one cloud does not qualify another.
