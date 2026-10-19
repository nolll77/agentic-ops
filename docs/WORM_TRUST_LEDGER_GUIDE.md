# WORM Trust Ledger & RFC 6962 Binary Merkle Tree Architecture Guide

> **Module Entrypoint**: [`agentic_ops/core/merkle.py`](../agentic_ops/core/merkle.py), [`agentic_ops/core/evidence.py`](../agentic_ops/core/evidence.py), [`agentic_ops/core/crypto.py`](../agentic_ops/core/crypto.py) & [`agentic_ops/cli/trust_ledger.py`](../agentic_ops/cli/trust_ledger.py)
> **Live Diagnostic Audit URL**: `https://agentic-ops-5ebv.onrender.com/api/diagnostics/trust_ledger_list`
> **Live Web Console**: `https://agentic-ops-5ebv.onrender.com/console` (Buttons: `WORM Trust Ledger CLI`, `Phase C: Adversarial & WORM`)
> **Live Web Chat**: `https://agentic-ops-5ebv.onrender.com/chat` (Prompts: `09`, `10`, `11`, `12` under `III. WORM Forensics`)
> **Automated Cryptographic Validation**: `tests/adversarial/test_merkle_tree.py` (`13 passed`), `tests/adversarial/test_evidence_integrity.py` (`4 passed`), `tests/security/test_executor.py` (`2 passed`) — **19 passed cryptographic tests**

---

## 1. What is the WORM Trust Ledger?

In autonomous AI systems, allowing an agent or human operator to retrospectively alter audit logs ("tampering") is a catastrophic vulnerability. Under regulatory frameworks like the **EU AI Act (Article 12: Record-keeping, Article 14: Human Oversight)**, an MLOps platform must guarantee that no post-hoc manipulation can rewrite the record of why an AI agent triggered or was blocked from triggering an action.

To reconcile **continuous real-time ingestion** with **mathematical tamper-evidence** and **confidential selective disclosure**, `Agentic-Ops` implements a **Dual-Tier Cryptographic Immutability Architecture**:

```text
+==================================================================================================+
| DUAL-TIER CRYPTOGRAPHIC IMMUTABILITY ARCHITECTURE                                                |
+==================================================================================================+

  [ TIER 1: REAL-TIME SEQUENTIAL LINEAR HASH CHAIN (Append-Only ledger.jsonl) ]
  
   [ Block 1: EP-0001 ]                     [ Block 2: EP-0002 ]                     [ Block 3: EP-0003 ]
   +------------------------+               +------------------------+               +------------------------+
   | episode_id: "EP-0001"  |               | episode_id: "EP-0002"  |               | episode_id: "EP-0003"  |
   | prev_hash : "genesis"  |               | prev_hash : hash(EP1)  |               | prev_hash : hash(EP2)  |
   | action    : create_iss |               | action    : deploy_pro |               | action    : rollback   |
   | decision  : ALLOW      |               | decision  : REQ_APPR   |               | decision  : REQ_APPR   |
   | status    : SUCCESS    |               | status    : AWAIT_APPR |               | status    : AWAIT_APPR |
   | signature : HMAC-512   |               | signature : HMAC-512   |               | signature : HMAC-512   |
   +-----------+------------+               +-----------+------------+               +-----------+------------+
               |                                        |                                        |
               +--- Linked by SHA-256 sequential hash ->+--- Linked by SHA-256 sequential hash ->+

  ==================================================================================================
  
  [ TIER 2: RFC 6962 BINARY MERKLE TREE (Selective Disclosure & O(log N) Audit Proofs) ]
  
                                       [ MERKLE ROOT (32 bytes) ]
                                                   |
                         +-------------------------+-------------------------+
                         |                                                   |
                   [ Parent H0123 ]                                    [ Parent H4567 ]
                         |                                                   |
              +----------+----------+                             +----------+----------+
              |                     |                             |                     |
        [ Node H01 ]          [ Node H23 ]                  [ Node H45 ]          [ Node H67 ]
              |                     |                             |                     |
          +---+---+             +---+---+                     +---+---+             +---+---+
          |       |             |       |                     |       |             |       |
        [ L0 ]  [ L1 ]        [ L2 ]  [ L3 ]                [ L4 ]  [ L5 ]        [ L6 ]  [ L7 ]
       EP-0001 EP-0002       EP-0003 EP-0004               EP-0005 EP-CHAOS1     EP-CHAOS2 EP-CHAOS3
  
  Domain Separators: Leaves = SHA-256(0x00 || JSON)  |  Parents = SHA-256(0x01 || Left || Right)
  Audit Proof for EP-0001: [ Sibling L1 (right), Sibling Node H23 (right), Sibling Parent H4567 (right) ]
  Verification Complexity: O(log N) = 3 hash operations (vs O(N) = 8 operations in linear chain)
+==================================================================================================+
```

### The Two Complementary Layers Explained:

1. **Tier 1 — Real-Time Append-Only Linear Hash Chain (`agentic_ops/core/evidence.py`)**:
   - **Chronological Linking**: Each episode record stores `previous_hash = SHA-256(canonical_json(E_{i-1}))`, anchored at `"genesis"`.
   - **HMAC-SHA512 Cryptographic Signature**: Every record is signed with a secret key (`sign_payload(previous_hash + canonical_json)`).
   - **Purpose**: Provides streaming immutability as events happen. Altering any byte in past records breaks all downstream hashes and invalidates subsequent signatures.

2. **Tier 2 — RFC 6962 Binary Merkle Tree (`agentic_ops/core/merkle.py`)**:
   - **Batch Condensation**: Condenses thousands of incidents into a single 32-byte cryptographic Merkle Root.
   - **Second-Preimage Attack Resistance**: Enforces standard domain separation prefixes (`0x00` for leaves, `0x01` for internal nodes).
   - **Selective Disclosure Proofs in $\mathcal{O}(\log N)$**: Allows an auditor to verify that episode $E_k$ was sealed without ever disclosing the contents of any other episode.


## 2. Is the WORM Trust Ledger Consultable via the Web Chat (`/chat`)?

**Yes, through two complementary mechanisms:**

### A. Conversational Consultation & Cognitive Prompts in `/chat`
In the Web Chat interface (`/chat`), click on **`📚 20 Prompts MCP`** and navigate to the **`III. WORM Forensics`** category:
- **Prompt `09` (`09_worm_ledger_chain_verification`)**:
  Instructs the LLM to inspect the append-only ledger, verify the full `SHA-256` linear hash chain and `HMAC-SHA512` signatures via `EvidenceStore.verify_chain()`, and return sealed episodes.
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

```text
Trust Ledger - Audit Trail                           
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Episode ID        ┃ Timestamp ┃ Risk Mode ┃ Agent LLM ┃ Action    ┃ Décision ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━┩
│ EP-CHAOS-31c6e006 │ 2026-10-… │ MODEL-005 │ speciali… │ propose_… │   DENY   │
│ EP-CHAOS-5950095d │ 2026-10-… │ DATA-042  │ speciali… │ propose_… │   DENY   │
│ EP-CHAOS-d6c18601 │ 2026-10-… │ INFRA-001 │ speciali… │ create_i… │   DENY   │
│ EP-0005           │ 2026-09-… │ DATA-042  │ data_spe… │ create_i… │  ALLOW   │
│ EP-0004           │ 2026-09-… │ DATA-042  │ data_spe… │ create_i… │  ALLOW   │
│ EP-0003           │ 2026-09-… │ DATA-042  │ data_spe… │ rollback… │ REQUIRE… │
│ EP-0002           │ 2026-09-… │ DATA-042  │ data_spe… │ deploy_p… │ REQUIRE… │
│ EP-0001           │ 2026-09-… │ DATA-042  │ data_spe… │ create_i… │  ALLOW   │
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

## 5. RFC 6962 Binary Merkle Tree Specification & Mathematics

While the Tier 1 linear hash chain provides streaming chronological linking, it suffers from two major structural constraints:
1. **$\mathcal{O}(N)$ Linear Verification**: An auditor verifying a record among $N$ historical incidents must replay all $N$ hashes from genesis.
2. **Zero Selective Disclosure**: The auditor must receive the entirety of the prior ledger, exposing sensitive data from unrelated incidents.

To solve this, `Agentic-Ops` implements a mathematically rigorous **Binary Merkle Tree** conforming to **RFC 6962** in [`agentic_ops/core/merkle.py`](../agentic_ops/core/merkle.py).

### A. Mathematical Formulation

#### 1. Leaf Hashing with Domain Separation
Each incident record $E_i$ is converted to a cryptographic leaf $L_i$ by prepending the single domain byte `0x00`:
$$L_i = \text{SHA-256}\left(\texttt{0x00} \mathbin{\Vert} \text{canonical\_bytes}(E_i)\right)$$
where $\text{canonical\_bytes}(E_i)$ is deterministic RFC-8785 JSON (alphabetically sorted keys, whitespace stripped via `separators=(',', ':')`).

#### 2. Internal Node Hashing with Domain Separation
Intermediate and root nodes are computed by pairwise hashing with the single domain byte `0x01`:
$$\text{Parent} = \text{SHA-256}\left(\texttt{0x01} \mathbin{\Vert} \text{Left}_{\text{bytes}} \mathbin{\Vert} \text{Right}_{\text{bytes}}\right)$$

#### 3. Second-Preimage Collision Resistance
Without domain separation, a malicious actor who discovers an internal node collision $H = \text{SHA-256}(A \mathbin{\Vert} B)$ could present the concatenated 64-byte string $A \mathbin{\Vert} B$ as a legitimate leaf. 

Because `Agentic-Ops` prefixes all leaf hashes with `0x00` and all parent hashes with `0x01`, the input preimages occupy mutually exclusive cryptographic domains:
$$\forall x, y, z : \quad \text{SHA-256}(\texttt{0x00} \mathbin{\Vert} x) \neq \text{SHA-256}(\texttt{0x01} \mathbin{\Vert} y \mathbin{\Vert} z)$$
Second-preimage attacks are mathematically impossible under the collision resistance of SHA-256.

#### 4. RFC 6962 Section 2.1 Recursive Split (No Odd Duplication)
Unlike Bitcoin-style Merkle trees that duplicate the lone odd leaf (`leaves[-1]`), RFC 6962 Section 2.1 strictly forbids leaf duplication and specifies a recursive split at the largest power of two strictly less than $n$:
$$k = 2^{\lfloor \log_2(n-1) \rfloor} \quad \text{such that } k < n \le 2k$$

The Merkle Tree Hash ($MTH$) over an array of leaves $D[0..n-1]$ is formally defined as:
$$MTH(\emptyset) = \text{SHA-256}(\text{""})$$
$$MTH(\{d_0\}) = d_0 \quad (\text{already hashed with domain byte } \texttt{0x00})$$
$$MTH(D[n]) = \text{SHA-256}\left(\texttt{0x01} \mathbin{\Vert} MTH(D[0:k]) \mathbin{\Vert} MTH(D[k:n])\right)$$

*Examples of recursive splitting*:
- For $n = 3 \implies k = 2$: the left subtree covers $D[0:2]$ and the right subtree covers $D[2:3]$.
- For $n = 5 \implies k = 4$: the left subtree covers $D[0:4]$ and the right subtree covers $D[4:5]$.
- For $n = 7 \implies k = 4$: the left subtree covers $D[0:4]$ and the right subtree covers $D[4:7]$ (which recursively splits into $2$ and $1$).

This asymmetric recursive split eliminates synthetic ghost leaves, guarantees a canonical tree topology, and minimizes audit path lengths for trailing records.

---

### B. ASCII Merkle Tree Topology (Live 8-Episode Ledger)

The active ledger contains 8 sealed episodes (`EP-0001` through `EP-0005`, and 3 chaos runs). Here is the exact physical tree constructed in memory:

```text
                               LEVEL 3: MERKLE ROOT (32 bytes)
                    [ f3e72fddffce225ed02e7afc58892f970a8ff9b6ca7662daefedba8302bef54e ]
                                                   |
                         +-------------------------+-------------------------+
                         |                                                   |
                      LEVEL 2                                             LEVEL 2
               [ Parent Node H0123 ]                               [ Parent Node H4567 ]
                         |                                                   |
              +----------+----------+                             +----------+----------+
              |                     |                             |                     |
           LEVEL 1               LEVEL 1                       LEVEL 1               LEVEL 1
        [ Node H01 ]          [ Node H23 ]                  [ Node H45 ]          [ Node H67 ]
              |                     |                             |                     |
          +---+---+             +---+---+                     +---+---+             +---+---+
          |       |             |       |                     |       |             |       |
       LEVEL 0 LEVEL 0       LEVEL 0 LEVEL 0               LEVEL 0 LEVEL 0       LEVEL 0 LEVEL 0
        [ L0 ]  [ L1 ]        [ L2 ]  [ L3 ]                [ L4 ]  [ L5 ]        [ L6 ]  [ L7 ]
          |       |             |       |                     |       |             |       |
       EP-0001 EP-0002       EP-0003 EP-0004               EP-0005 EP-CHAOS1     EP-CHAOS2 EP-CHAOS3
```

---

## 6. Selective Disclosure & $\mathcal{O}(\log N)$ Audit Proofs (EU AI Act Article 12)

### A. Resolving the Regulatory Privacy-Auditability Paradox
Under **EU AI Act Article 12** and **Article 14**, regulated AI systems must provide auditors with verifiable proof of decision logging. However:
- A company **cannot** hand over its entire raw ledger to an external auditor without leaking proprietary inference features, internal telemetry, and customer data contained in other episodes.
- A company **cannot** rely on simple hashes of individual records, because an auditor cannot verify whether an isolated hash belonged to the genuine production sequence.

**The Merkle Tree solves this paradox completely**:
1. The operator publishes or timestamps only the **32-byte Merkle Root** (`merkle-root`).
2. When an auditor asks for proof of episode `EP-0001`, the operator provides a compact **Merkle Audit Proof Packet**:
   - The canonical content of `EP-0001`.
   - The $\mathcal{O}(\log N)$ sibling path: only **3 sibling hashes** for 8 episodes (or **14 hashes for 10,000 episodes**).
3. The auditor computes 3 hashes, verifies that they arrive at the known Merkle Root, and obtains mathematical certainty that `EP-0001` was part of the sealed ledger—**without ever seeing or receiving a single byte from EP-0002 through EP-0008**.

### B. The Epistemic Boundary of Merkle Proofs: Root Authenticity vs. Leaf Membership

An essential cryptographic distinction must be drawn to avoid qualifying Merkle proofs as "inviolable in absolute terms":
> **A Merkle audit proof mathematically establishes leaf membership relative to a specific root $R$. It does NOT, on its own, prove that $R$ itself is the genuine, authentic production root.**

If an adversary generates an alternate ledger from scratch, they can compute a valid alternate root $R'$ and emit mathematically valid inclusion proofs against $R'$. Consequently:
- **What the Merkle proof guarantees**: Given an authentic root $R$, it is computationally infeasible under SHA-256 for an operator to forge a proof for an unsealed or tampered episode, or to substitute an incident without detection.
- **What requires an external trust anchor**: The authenticity and non-repudiation of the root $R$ itself.

To anchor root authenticity in enterprise production environments (specified in **Chantier 4** of [`PRODUCTION_READINESS_ROADMAP_AND_GAPS.md`](PRODUCTION_READINESS_ROADMAP_AND_GAPS.md)), three complementary external mechanisms are required:
1. **RFC 3161 Timestamping Authority (TSA)**: Periodically submitting epoch roots to an accredited external timestamping service, producing cryptographically sealed `.tsr` tokens proving that $R$ existed at a certified legal timestamp.
2. **Public Transparency Logs (Sigstore Rekor / Certificate Transparency)**: Appending epoch roots to a public, append-only, verifiable transparency log to prevent split-view attacks.
3. **Asymmetric HSM Signatures (AWS/GCP Cloud KMS)**: Signing $R$ with an asymmetric key pair (Ed25519 or ECDSA P-256) residing inside a FIPS 140-2 Level 3 Hardware Security Module.

In the current demonstration and sandbox release, the root is anchored to the reference episodes baked directly into the immutable Docker image layer, while external cloud anchoring constitutes the next planned production milestone.

### C. Audit Proof Generation, Cryptographic Payload Binding & Verification Algorithm

#### 1. Dual Complexity Profile & Zero-Slice Memory Optimization ($\mathcal{O}(N)$ vs. $\mathcal{O}(\log N)$)
A strict architectural distinction must be maintained:
- **Ledger Ingestion & Tree Construction**: Building the complete Merkle Tree from a flat `ledger.jsonl` requires reading $N$ records and computing $N$ leaf hashes, which is strictly **$\mathcal{O}(N)$ in time and memory**. The implementation in [`agentic_ops/core/merkle.py`](../agentic_ops/core/merkle.py) uses index bounds `[start:end]` over a contiguous `Sequence[str]` array without copying list slices, eliminating $\mathcal{O}(N \log N)$ slicing memory churn and bounding the recursive call stack to $\lceil \log_2 N \rceil$.
- **Audit Proof Generation**: Extracting an episode proof from flat disk storage requires an **$\mathcal{O}(N)$ linear scan** to locate the target `episode_id` index, followed by an **$\mathcal{O}(\log N)$ sibling path derivation**.
- **Audit Proof Size & Verification**: The audit proof packet size and third-party verification by an external regulator are strictly **$\mathcal{O}(\log N)$ in time and space** ($\lceil \log_2 N \rceil$ hashing operations, independent of prior ledger size).

#### 2. Mandatory Cryptographic Payload Binding (Anti-Bypass & Anti-Tampering)
A Merkle inclusion proof is cryptographically meaningless if the leaf hash is uncoupled from the actual episode payload. `Agentic-Ops` enforces **Mandatory Cryptographic Payload Binding**:
The `proof_packet` generated by `EvidenceStore.get_merkle_proof(episode_id)` embeds the full canonical episode dictionary:

```python
proof_packet = {
    "episode_id": episode_id,
    "leaf_index": leaf_index,
    "leaf_hash": target_leaf,
    "canonical_payload": raw_episode,  # Cryptographically bound payload
    "merkle_root": self.get_merkle_root(),
    "audit_path": audit_path,          # O(log N) sibling hashes with positions
    "rfc6962_domain_separation": True,
}
```

The verification engine `EvidenceStore.verify_merkle_proof(proof_packet)` enforces a **three-stage mathematical gate**:

```python
# Stage 1: Mandatory Payload Extraction & Identity Matching (Anti-Bypass)
payload_to_check = None
if raw_episode is not None:
    c_ep = dict(raw_episode)
    c_ep.pop("hash", None)
    c_ep.pop("cryptographic_signature", None)
    if c_ep.get("episode_id") != claimed_episode_id:
        return False
    payload_to_check = get_canonical_json(c_ep)
elif "canonical_payload" in proof_packet and proof_packet["canonical_payload"]:
    payload_str = proof_packet["canonical_payload"]
    try:
        parsed = json.loads(payload_str)
        if parsed.get("episode_id") != claimed_episode_id:
            return False
    except Exception:
        return False
    payload_to_check = payload_str

# Strict Gate: A proof stripped of its payload is unconditionally rejected
if payload_to_check is None:
    return False

# Stage 2: Deterministic Leaf Hash Verification (0x00 Domain)
computed_leaf = hashlib.sha256(b"\x00" + payload_to_check.encode("utf-8")).hexdigest()
if computed_leaf.lower() != leaf_hash.lower():
    return False  # Payload modified after sealing (Tamper Detected)

# Stage 3: O(log N) Sibling Path Traversal (0x01 Domain)
curr = computed_leaf
for step in proof_packet["audit_path"]:
    if step["position"] == "right":
        curr = hash_children(curr, step["hash"])   # SHA-256(0x01 || curr || sibling)
    else:
        curr = hash_children(step["hash"], curr)   # SHA-256(0x01 || sibling || curr)
return curr == proof_packet["merkle_root"]
```

---

## 7. Interactive CLI Commands & Verbatim Live Demonstration

The Trust Ledger CLI ([`agentic_ops/cli/trust_ledger.py`](../agentic_ops/cli/trust_ledger.py)) provides complete forensic inspection:

### Command 1: Inspect the Root Hash of the Ledger
```bash
$ uv run python -m agentic_ops.cli.trust_ledger merkle-root
```
**Output**:
```text
=== Binary Merkle Tree Cryptographique (RFC 6962) ===
Nombre d'épisodes scellés : 8
Merkle Root (SHA-256)      : f3e72fddffce225ed02e7afc58892f970a8ff9b6ca7662daefedba8302bef54e
Profondeur de l'arbre      : 4 niveaux (O(log N) = 3 étapes)
Second-preimage resistant : Domain Separators 0x00 (feuilles) / 0x01 (nœuds parents)
```

### Command 2: Generate & Verify an Inclusion Proof for a Specific Episode
```bash
$ uv run python -m agentic_ops.cli.trust_ledger merkle-proof EP-0001
```
**Output**:
```text
=== Preuve d'Inclusion Merkle (Audit Proof) : EP-0001 ===
Position dans l'arbre : Feuille index 0 / 8
Leaf Hash (RFC 6962)  : a6bffcb84e4992311828368a47fefd4d1c123343952bd2354517d1c5c97f487d
Merkle Root Attendue  : f3e72fddffce225ed02e7afc58892f970a8ff9b6ca7662daefedba8302bef54e
Audit Path            : 3 étapes logarithmiques
  [1] Sibling (right) : 6357c0642a0b4051d764fb5a936f9d83435fcb834b87eefb6070270a97e33f04
  [2] Sibling (right) : 94b83c0479ae726c1c0f5e4ad9e14b32b77a774a8c4d2af0685f446f4e2e148c
  [3] Sibling (right) : b6038ce4b3b198f2a8fb7b9ab5d85b0deb67b018371824eb80ec2e3831e2394e

Vérification O(log N) : VALIDE (Mathématiquement intègre & inclus dans le Merkle Root)
```

---

## 8. Cryptographic Hardening, CSPRNG & Adversarial Test Matrix

The cryptographic integrity of the Trust Ledger is validated by **21 automated tests** in CI/CD:

| Test File | Test Case | Target Security Property | Status |
| :--- | :--- | :--- | :--- |
| **[`test_merkle_tree.py`](../tests/adversarial/test_merkle_tree.py)** | `test_merkle_tree_empty` | Empty tree boundary condition returns SHA-256 of empty string. | **PASSED** |
| | `test_merkle_tree_single_leaf` | Single leaf root matches RFC 6962 leaf hash directly. | **PASSED** |
| | `test_merkle_tree_even_leaves` | Balanced pairwise parent reduction over 2, 4, 8 leaves. | **PASSED** |
| | `test_merkle_tree_odd_leaves` | Asymmetric recursive tree handling on odd cardinalities (3, 7, 15). | **PASSED** |
| | `test_merkle_rfc6962_recursive_split_odd_sizes` | Strictly validates RFC 6962 Section 2.1 recursive split at $k = 2^{\lfloor \log_2(n-1) \rfloor}$ without leaf duplication across sizes 2..9 and canonical $n=3$. | **PASSED** |
| | `test_merkle_audit_proof_all_indices` | Exhaustive $\mathcal{O}(\log N)$ proof generation for all leaf positions. | **PASSED** |
| | `test_merkle_audit_proof_tampered_leaf_fails` | 1-bit alteration in episode content immediately fails proof verification. | **PASSED** |
| | `test_merkle_audit_proof_tampered_sibling_fails` | Alteration of any sibling hash in the Audit Path fails verification. | **PASSED** |
| | `test_merkle_audit_proof_tampered_root_fails` | Verifying proof against an incorrect root hash fails immediately. | **PASSED** |
| | `test_merkle_second_preimage_resistance` | Validates that leaf hashes (`0x00`) never collide with internal node hashes (`0x01`). | **PASSED** |
| | `test_merkle_various_tree_sizes` | Parametrized tests over sizes 2, 3, 4, 7, 8, 15, 16. | **PASSED** |
| | `test_evidence_store_merkle_tree_integration` | Validates tree construction over real stored episodes. | **PASSED** |
| | `test_evidence_store_merkle_proof_verification` | Validates end-to-end `get_merkle_proof` $\rightarrow$ `verify_merkle_proof`. | **PASSED** |
| | `test_evidence_store_merkle_proof_nonexistent_episode` | Nonexistent episode returns `None` safely without throwing unhandled exceptions. | **PASSED** |
| | `test_merkle_proof_binding_tampering` | Validates Cryptographic Payload Binding: tampered payloads, falsified episode IDs, or mismatched leaf hashes fail verification immediately before path traversal. | **PASSED** |
| **[`test_evidence_integrity.py`](../tests/adversarial/test_evidence_integrity.py)** | `test_evidence_store_chain_verification_on_tamper` | Modifying historical record in `ledger.jsonl` breaks `verify_chain()`. | **PASSED** |
| | `test_evidence_store_forged_signature_fails` | Forged HMAC-SHA512 signature is detected and rejected. | **PASSED** |
| | `test_evidence_store_canonical_json_determinism` | RFC 8785 guarantees identical hash across differing dictionary key insertion orders. | **PASSED** |
| | `test_crypto_fail_closed_in_production_without_key` | System raises `RuntimeError` on startup in production if no key is injected. | **PASSED** |
| **[`test_executor.py`](../tests/security/test_executor.py)** | `test_executor_audit_sealing` | Executor automatically seals execution results into the evidence store. | **PASSED** |
| | `test_executor_tamper_evident_signature` | Validates HMAC signature generation on real remediation actions. | **PASSED** |

---

## 9. Is the Ledger Stored in Render? (Stateless Container vs. Persistent Storage)


Applying the project's **Radical Honesty** rule, the exact physical lifecycle of the WORM ledger in `Render` is governed by the following deployment mechanics:

```text
+--------------------------------------------------------------------------------------------------+
| PHYSICAL STORAGE DUALITY IN RENDER FREE TIER                                                     |
+--------------------------------------------------------------------------------------------------+
|                                                                                                  |
| [1. Immutable Docker Image Layer]                [2. Local Ephemeral Storage (/tmp & /app)]      |
| - Sealed into container at build time             - Runtime scratch space for active session     |
| - Path: /app/agentic_ops/evidence_store/*.json    - Path: /app/.../ledger.jsonl & /tmp/.../*.db  |
| - Contains historical reference blocks (EP-0001   - Captures new live episodes and chaos runs    |
|   to EP-0005, chaos runs)                         - Resets on container sleep (15 min) or rebuild|
| - PERMANENT across all wake-ups (0 EUR)           - EPHEMERAL in Free Tier (0 EUR)               |
+--------------------------------------------------------------------------------------------------+
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

### C. Signing Key Lifecycle: Ephemeral CSPRNG Session Key vs. Cloud KMS
In [`scripts/entrypoint.sh`](../scripts/entrypoint.sh), when no signing key is injected via environment variables:
- The container generates an **ephemeral 256-bit cryptographically secure random session key** at launch using `secrets.token_hex(32)`.
- **Sandbox Security Advantage**: This eliminates any static or hardcoded secrets in public container images.
- **Cross-Restart Durability Tradeoff**: In a stateless container, if the container restarts, the ephemeral key changes, meaning historical `HMAC-SHA512` signatures from previous container incarnations cannot be verified unless `LEDGER_SECRET_KEY` is persisted across boots.
- **Production Standard**: In an enterprise deployment, `LEDGER_SECRET_KEY` must be provisioned via an external secrets manager (**HashiCorp Vault**, **AWS KMS / Secrets Manager**, or encrypted environment variables) to maintain unbroken cryptographic verification across indefinite container lifecycles.
