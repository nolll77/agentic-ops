# WORM Trust Ledger Forensics & Audit Guide

> **Module Entrypoint**: `agentic_ops/core/evidence.py`, `agentic_ops/core/crypto.py` & `agentic_ops/cli/trust_ledger.py`
> **Live Diagnostic Audit URL**: `https://agentic-ops-5ebv.onrender.com/api/diagnostics/trust_ledger_list`
> **Live Web Console**: `https://agentic-ops-5ebv.onrender.com/console` (Button: `WORM Trust Ledger CLI`)
> **Live Web Chat**: `https://agentic-ops-5ebv.onrender.com/chat` (Prompts: `09`, `10`, `11`, `12` under `III. WORM Forensics`)
> **Automated Cryptographic Validation**: `tests/security/test_evidence_store.py` (`6 passed`)

---

## 1. What is the WORM Trust Ledger?

In autonomous AI systems, allowing an agent or human operator to retrospectively alter audit logs ("tampering") is a critical security vulnerability. 

The **WORM (Write Once, Read Many) Trust Ledger** (`ledger.jsonl`) provides mathematical immutability for every remediation decision taken by `Agentic-Ops`. Every incident episode is:
1. **Canonicalized**: Transformed into RFC-8785 canonical JSON (`get_canonical_json`) to eliminate key-ordering discrepancies.
2. **Chained with Previous Block (`previous_hash`)**: Each episode contains the `SHA-256` hash of the preceding block, forming an unbroken cryptographic Merkle chain starting from `"genesis"`.
3. **Signed with HMAC-SHA512**: Digitally signed using a secret key (`sign_payload(previous_hash + canonical_json)`).
4. **Appended in WORM Storage**: Written via append-only mode (`open(..., "a")`) into `agentic_ops/evidence_store/ledger.jsonl`.

```ansi
[1;34m+--------------------------------------------------------------------------------------------------+[0m
[1;34m|[0m [1;36m[1mCRYPTOGRAPHIC WORM CHAIN TOPOLOGY[0m [1;34m|[0m
[1;34m+--------------------------------------------------------------------------------------------------+[0m
                                                                                                   
 [ Block 1: EP-0001 ]                     [ Block 2: EP-0002 ]                     [ Block 3: EP-0003 ]
 +------------------------+               +------------------------+               +------------------------+
[1;34m|[0m episode_id: "EP-0001"  |               | episode_id: "EP-0002"  |               | episode_id: "EP-0003"  [1;34m|[0m
[1;34m|[0m prev_hash : "genesis"  |               | prev_hash : hash(EP1)  |               | prev_hash : hash(EP2)  [1;34m|[0m
[1;34m|[0m action    : create_iss |               | action    : deploy_pro |               | action    : rollback   [1;34m|[0m
[1;34m|[0m decision  : ALLOW      |               | decision  : REQ_APPR   |               | decision  : REQ_APPR   [1;34m|[0m
[1;34m|[0m status    : SUCCESS    |               | status    : AWAIT_APPR |               | status    : AWAIT_APPR [1;34m|[0m
[1;34m|[0m signature : HMAC-512   |               | signature : HMAC-512   |               | signature : HMAC-512   [1;34m|[0m
 +-----------+------------+               +-----------+------------+               +-----------+------------+
[1;34m|[0m                                        |                                        [1;34m|[0m
             +---- Linked by Merkle hash ----------[1;33m-[1;36m->[0m[0m+---- Linked by Merkle hash ----------[1;33m-[1;36m->[0m[0m+
```

---

## 2. Is the WORM Trust Ledger Consultable via the Web Chat (`/chat`)?

**Yes, through two complementary mechanisms:**

### A. Conversational Consultation & Cognitive Prompts in `/chat`
In the Web Chat interface (`/chat`), click on **`📚 20 Prompts MCP`** and navigate to the **`III. WORM Forensics`** category:
- **Prompt `09` (`09_worm_ledger_chain_verification`)**:
  Instructs the LLM to inspect the append-only ledger, verify the full `SHA-256` Merkle chain and `HMAC-SHA512` signatures via `EvidenceStore.verify_chain()`, and return sealed episodes.
- **Prompt `10` (`10_worm_simulate_and_seal_episode`)**:
  Simulates an incident episode, traces the `PolicyEngine` evaluation, and explains how the cryptographic signature is generated.
- **Prompt `11` (`11_worm_tamper_detection_audit`)**:
  Requests an explanation and audit of how altering a single byte in a sealed record breaks mathematical verification.
- **Prompt `12` (`12_worm_eu_ai_act_compliance_report`)**:
  Generates a formal compliance audit mapping `ledger.jsonl` records to EU AI Act Article 12 (Record-keeping) and Article 14 (Human Oversight).

### B. Direct Live Query in Natural Language
You can ask the chat directly:
- *"Quels sont les épisodes scellés dans le grand livre WORM ?"*
- *"Pourquoi l'épisode EP-0003 sur DATA-042 a été mis en attente d'approbation humaine ?"*
- *"Est-ce que le grand livre est intègre mathématiquement ?"*

The chat model reads the governance context and synthesizes an SRE explanation.

---

## 3. How to Consult the Raw WORM Ledger Data (3 Methods)

For auditors, SREs, and compliance officers needing raw, verbatim forensic evidence:

### Method 1: The Interactive SRE Web Console (`/console`) — 1 Click
Open **[`https://agentic-ops-5ebv.onrender.com/console`](https://agentic-ops-5ebv.onrender.com/console)**:
- Click the button **`WORM Trust Ledger CLI`**.
- It directly invokes `python -m agentic_ops.cli.trust_ledger list` inside the Render cloud container and outputs the sealed table:

```ansi
Trust Ledger - Audit Trail                           
[1;34m┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━┓[0m
[1;34m┃[0m Episode ID        [1;34m┃[0m Timestamp [1;34m┃[0m Risk Mode [1;34m┃[0m Agent LLM [1;34m┃[0m Action    [1;34m┃[0m Décision [1;34m┃[0m
[1;34m┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━┩[0m
[1;34m│[0m EP-[1;36mCHAOS-31[0mc6e006 [1;34m│[0m 2026-10-… [1;34m│[0m [1;36mMODEL-005[0m [1;34m│[0m speciali… [1;34m│[0m propose_… [1;34m│[0m   [1;31mDENY[0m   [1;34m│[0m
[1;34m│[0m EP-[1;36mCHAOS-5950095[0md [1;34m│[0m 2026-10-… [1;34m│[0m [1;36mDATA-042[0m  [1;34m│[0m speciali… [1;34m│[0m propose_… [1;34m│[0m   [1;31mDENY[0m   [1;34m│[0m
[1;34m│[0m EP-CHAOS-d6c18601 [1;34m│[0m 2026-10-… [1;34m│[0m [1;36mINFRA-001[0m [1;34m│[0m speciali… [1;34m│[0m create_i… [1;34m│[0m   [1;31mDENY[0m   [1;34m│[0m
[1;34m│[0m [1;36mEP-0005[0m           [1;34m│[0m 2026-09-… [1;34m│[0m [1;36mDATA-042[0m  [1;34m│[0m data_spe… [1;34m│[0m create_i… [1;34m│[0m  [1;32mALLOW[0m   [1;34m│[0m
[1;34m│[0m [1;36mEP-0004[0m           [1;34m│[0m 2026-09-… [1;34m│[0m [1;36mDATA-042[0m  [1;34m│[0m data_spe… [1;34m│[0m create_i… [1;34m│[0m  [1;32mALLOW[0m   [1;34m│[0m
[1;34m│[0m [1;36mEP-0003[0m           [1;34m│[0m 2026-09-… [1;34m│[0m [1;36mDATA-042[0m  [1;34m│[0m data_spe… [1;34m│[0m rollback… [1;34m│[0m [1;33mREQUIRE[0m… [1;34m│[0m
[1;34m│[0m [1;36mEP-0002[0m           [1;34m│[0m 2026-09-… [1;34m│[0m [1;36mDATA-042[0m  [1;34m│[0m data_spe… [1;34m│[0m deploy_p… [1;34m│[0m [1;33mREQUIRE[0m… [1;34m│[0m
[1;34m│[0m [1;36mEP-0001[0m           [1;34m│[0m 2026-09-… [1;34m│[0m [1;36mDATA-042[0m  [1;34m│[0m data_spe… [1;34m│[0m create_i… [1;34m│[0m  [1;32mALLOW[0m   [1;34m│[0m
└───────────────────┴───────────┴───────────┴───────────┴───────────┴──────────┘
```

### Method 2: Direct REST API Inspection
From any terminal or CI/CD script:
```bash
# Read the formatted audit trail
curl -s https://agentic-ops-5ebv.onrender.com/api/diagnostics/trust_ledger_list

# Verify cryptographic tampering detection (Phase C)
curl -s https://agentic-ops-5ebv.onrender.com/api/diagnostics/sandbox_phase_c_adversarial_worm
```

### Method 3: Via Connected MCP Clients (`inspect_worm_trust_ledger`)
When using `Claude Desktop`, `Cursor`, `Windsurf`, or `Google Antigravity` over MCP (`POST /mcp`):
The client calls the tool `inspect_worm_trust_ledger`:
```json
{
  "name": "inspect_worm_trust_ledger",
  "arguments": {
    "limit": 10,
    "verify_cryptographic_signatures": true
  }
}
```
The server runs `EvidenceStore.verify_chain()`, validates every hash against `expected_previous`, verifies `HMAC-SHA512` signatures, and streams the verified blocks into the AI conversation.

---

## 4. Tamper-Evident Verification Algorithm (`verify_chain`)

The exact verification algorithm in [`agentic_ops/core/evidence.py`](../agentic_ops/core/evidence.py) executes as follows:

```python
def verify_chain(self) -> bool:
    expected_previous = "genesis"
    with open(self.ledger_file, "r") as f:
        for line_no, line in enumerate(f, 1):
            ep = json.loads(line)
            sig = ep.pop("cryptographic_signature", None)
            ep.pop("hash", None)
            prev = ep.get("previous_hash")
            
            # 1. Verify chronological block linking
            if prev != expected_previous:
                return False  # Chain linkage break
                
            # 2. Verify payload signature with secret key
            canonical = get_canonical_json(ep)
            payload_to_verify = prev + canonical
            if not verify_signature(payload_to_verify, sig):
                return False  # Content altered or signature forged
                
            expected_previous = hashlib.sha256(canonical.encode('utf-8')).hexdigest()
            
    return True
```

If an attacker modifies even a single comma or timestamp in `ledger.jsonl`, `verify_chain()` immediately returns `False` and flags the corrupted block.

---

## 5. Is the Ledger Stored in Render? (Stateless Container vs. Persistent Storage)

Applying the project's **Radical Honesty** rule, the exact physical lifecycle of the WORM ledger in `Render` is governed by the following deployment mechanics:

```ansi
[1;34m+--------------------------------------------------------------------------------------------------+[0m
[1;34m|[0m [1;36m[1mPHYSICAL STORAGE DUALITY IN RENDER FREE TIER[0m [1;34m|[0m
[1;34m+--------------------------------------------------------------------------------------------------+[0m
[1;34m|[0m                                                                                                  [1;34m|[0m
[1;34m|[0m [1. Immutable Docker Image Layer]                [2. Local Ephemeral Storage (/tmp & /app)]      [1;34m|[0m
[1;34m|[0m - Sealed into container at build time             - Runtime scratch space for active session     [1;34m|[0m
[1;34m|[0m - Path: /app/agentic_ops/evidence_store/*.json    - Path: /app/.../ledger.jsonl & /tmp/.../*.db  [1;34m|[0m
[1;34m|[0m - Contains historical reference blocks (EP-0001   - Captures new live episodes and chaos runs    [1;34m|[0m
[1;34m|[0m   to EP-0005, chaos runs)                         - Resets on container sleep (15 min) or rebuild[1;34m|[0m
[1;34m|[0m - PERMANENT across all wake-ups ([1;32m0 EUR[0m)           - EPHEMERAL in [1;32mFree Tier[0m ([1;32m0 EUR[0m)               [1;34m|[0m
[1;34m+--------------------------------------------------------------------------------------------------+[0m
```

### A. The Reference Archive: Sealed Inside the Docker Image Layer
During container build (`Dockerfile`), the repository sources are baked into the container image:
```dockerfile
COPY agentic_ops/ ./agentic_ops/
```
As a result, the reference baseline episodes (`EP-0001` through `EP-0005`, and chaos episodes `EP-CHAOS-31c6e006`, `EP-CHAOS-5950095d`, `EP-CHAOS-d6c18601`) reside permanently in:
```bash
/app/agentic_ops/evidence_store/
```
They **never disappear**, even when the container spins down after 15 minutes of inactivity or when Render restarts the container.

### B. The Live Execution Ledger: Ephemeral vs. Persistent Disks
At runtime, whenever new remediation episodes or live tests run:
1. **Append-Only File**: `agentic_ops/evidence_store/ledger.jsonl` receives newly signed entries.
2. **Approval SQLite Store**: `/tmp/state/approvals.db` tracks transactional human approvals.

**In the Render Free Tier (`0 EUR`)**:
- Render's free tier provides an **ephemeral local filesystem** (`Stateless Container`).
- If the instance goes to sleep (after 15 minutes of HTTP silence) and wakes up later, newly generated runtime entries reset back to the immutable Docker image state.

**In Enterprise Production Deployments**:
- Production instances attach a **Render Persistent Disk** mounted at `/app/agentic_ops/evidence_store` (or stream sealed blocks to an external WORM object store like **AWS S3 Object Lock** or **GCS Retention Policies**).
- For our live demonstration and academic jury defense, sealing the reference audit episodes directly into the Docker image guarantees that every auditor accessing `/console` (`WORM Trust Ledger CLI`) sees the certified audit trail 24/7 without requiring paid cloud disks.
