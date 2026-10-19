import pytest
import hashlib
import json
from pathlib import Path

from agentic_ops.core.merkle import MerkleTree, hash_leaf, hash_children
from agentic_ops.core.evidence import EvidenceStore


def test_merkle_empty_tree():
    tree = MerkleTree([])
    assert len(tree.root) == 64
    assert tree.root == hashlib.sha256(b"").hexdigest()


def test_merkle_single_leaf():
    leaf_data = {"incident": "INC-001", "action": "deny"}
    tree = MerkleTree([leaf_data])
    assert tree.root == hash_leaf(leaf_data)
    proof = tree.get_audit_proof(0)
    assert len(proof) == 0
    assert MerkleTree.verify_audit_proof(leaf_data, proof, tree.root) is True


def test_merkle_two_leaves():
    leaves = ["leaf_0", "leaf_1"]
    tree = MerkleTree(leaves)
    h0 = hash_leaf("leaf_0")
    h1 = hash_leaf("leaf_1")
    expected_root = hash_children(h0, h1)
    assert tree.root == expected_root

    # Proof for leaf 0
    proof_0 = tree.get_audit_proof(0)
    assert len(proof_0) == 1
    assert proof_0[0] == {"position": "right", "hash": h1}
    assert MerkleTree.verify_audit_proof("leaf_0", proof_0, tree.root) is True

    # Proof for leaf 1
    proof_1 = tree.get_audit_proof(1)
    assert len(proof_1) == 1
    assert proof_1[0] == {"position": "left", "hash": h0}
    assert MerkleTree.verify_audit_proof("leaf_1", proof_1, tree.root) is True


def test_merkle_odd_leaves():
    leaves = [f"event_{i}" for i in range(3)]
    tree = MerkleTree(leaves)
    assert len(tree.root) == 64

    # Verify proofs for all 3 leaves
    for idx, leaf in enumerate(leaves):
        proof = tree.get_audit_proof(idx)
        assert MerkleTree.verify_audit_proof(leaf, proof, tree.root) is True


@pytest.mark.parametrize("n_leaves", [4, 7, 8, 15, 16])
def test_merkle_variable_leaf_counts(n_leaves):
    leaves = [{"id": f"INC-{i}", "val": i * 10} for i in range(n_leaves)]
    tree = MerkleTree(leaves)
    assert len(tree.root) == 64

    for idx, leaf in enumerate(leaves):
        proof = tree.get_audit_proof(idx)
        assert MerkleTree.verify_audit_proof(leaf, proof, tree.root) is True


def test_merkle_proof_tamper_leaf():
    leaves = ["event_A", "event_B", "event_C", "event_D"]
    tree = MerkleTree(leaves)
    proof = tree.get_audit_proof(1)

    # Tampered leaf data
    assert MerkleTree.verify_audit_proof("event_TAMPERED", proof, tree.root) is False


def test_merkle_proof_tamper_sibling():
    leaves = ["event_A", "event_B", "event_C", "event_D"]
    tree = MerkleTree(leaves)
    proof = tree.get_audit_proof(2)

    # Corrupt sibling hash in the audit path
    tampered_proof = list(proof)
    tampered_proof[0] = {"position": tampered_proof[0]["position"], "hash": "00" * 32}
    assert MerkleTree.verify_audit_proof("event_C", tampered_proof, tree.root) is False


def test_merkle_proof_tamper_root():
    leaves = ["event_A", "event_B"]
    tree = MerkleTree(leaves)
    proof = tree.get_audit_proof(0)
    fake_root = "ff" * 32
    assert MerkleTree.verify_audit_proof("event_A", proof, fake_root) is False


def test_evidence_store_merkle_integration(tmp_path):
    store = EvidenceStore(str(tmp_path / "evidence"))

    # Save 5 distinct episodes
    ep_ids = []
    for i in range(5):
        ep = {
            "episode_id": f"EP-TEST-{i:03d}",
            "risk_id": f"RISK-{i}",
            "action": "restart_pod" if i % 2 == 0 else "deny",
            "val": i,
        }
        store.save(ep)
        ep_ids.append(ep["episode_id"])

    # Build Merkle Tree
    tree = store.get_merkle_tree()
    root = store.get_merkle_root()
    assert len(root) == 64

    # Verify audit proofs for every episode in ledger
    for ep_id in ep_ids:
        proof_packet = store.get_merkle_proof(ep_id)
        assert proof_packet is not None
        assert proof_packet["episode_id"] == ep_id
        assert proof_packet["merkle_root"] == root
        assert len(proof_packet["audit_path"]) > 0
        assert EvidenceStore.verify_merkle_proof(proof_packet) is True

    # Non-existent episode returns None
    assert store.get_merkle_proof("EP-NON-EXISTENT") is None

    # Tampering: if we alter one line in ledger, tree root changes
    with open(store.ledger_file, "r") as f:
        lines = f.readlines()
    first_ep = json.loads(lines[0])
    first_ep["action"] = "tampered_mutation"
    lines[0] = json.dumps(first_ep) + "\n"
    with open(store.ledger_file, "w") as f:
        f.writelines(lines)

    new_root = store.get_merkle_root()
    assert new_root != root
    # Old proof packet fails against the new altered root
    proof_packet["merkle_root"] = new_root
    assert EvidenceStore.verify_merkle_proof(proof_packet) is False


def test_merkle_rfc6962_recursive_split_odd_sizes():
    """Validates strict adherence to RFC 6962 Section 2.1 (k = 2^floor(log2(n-1))) for non-power-of-two trees."""
    from agentic_ops.core.merkle import largest_power_of_two_less_than
    
    assert largest_power_of_two_less_than(2) == 1
    assert largest_power_of_two_less_than(3) == 2
    assert largest_power_of_two_less_than(4) == 2
    assert largest_power_of_two_less_than(5) == 4
    assert largest_power_of_two_less_than(6) == 4
    assert largest_power_of_two_less_than(7) == 4
    assert largest_power_of_two_less_than(8) == 4
    assert largest_power_of_two_less_than(9) == 8

    # For n = 3: left child is hash(L0, L1), right child is L2 directly (NO lone duplication)
    leaves = ["leaf_0", "leaf_1", "leaf_2"]
    tree = MerkleTree(leaves)
    h0 = hash_leaf("leaf_0")
    h1 = hash_leaf("leaf_1")
    h2 = hash_leaf("leaf_2")
    h01 = hash_children(h0, h1)
    manual_rfc_root = hash_children(h01, h2)
    assert tree.root == manual_rfc_root

    # Proof for leaf 2 (rightmost lone leaf) in RFC 6962: exactly 1 sibling (h01 on the left)
    proof_2 = tree.get_audit_proof(2)
    assert len(proof_2) == 1
    assert proof_2[0] == {"position": "left", "hash": h01}
    assert MerkleTree.verify_audit_proof("leaf_2", proof_2, tree.root) is True


def test_merkle_proof_binding_tampering(tmp_path):
    """Validates that verify_merkle_proof strictly binds episode_id and episode content to leaf_hash."""
    store = EvidenceStore(str(tmp_path / "evidence"))
    ep = {
        "episode_id": "EP-BIND-001",
        "action": "create_issue",
        "decision": "ALLOW",
        "details": {"metric": "drift_share", "val": 0.42},
    }
    store.save(ep)

    proof_packet = store.get_merkle_proof("EP-BIND-001")
    assert proof_packet is not None
    assert "canonical_payload" in proof_packet
    assert EvidenceStore.verify_merkle_proof(proof_packet) is True

    # 1. Tampering with canonical_payload (modifying action)
    tampered_packet = dict(proof_packet)
    tampered_payload = json.loads(tampered_packet["canonical_payload"])
    tampered_payload["action"] = "scale_to_zero"
    tampered_packet["canonical_payload"] = json.dumps(tampered_payload)
    assert EvidenceStore.verify_merkle_proof(tampered_packet) is False

    # 2. Tampering with claimed episode_id
    id_spoofed_packet = dict(proof_packet)
    id_spoofed_packet["episode_id"] = "EP-BIND-999"
    assert EvidenceStore.verify_merkle_proof(id_spoofed_packet) is False

    # 3. Providing an external raw_episode that does not match
    fake_raw_ep = dict(ep)
    fake_raw_ep["details"]["val"] = 0.99
    assert EvidenceStore.verify_merkle_proof(proof_packet, raw_episode=fake_raw_ep) is False

    # 4. Stripping canonical_payload completely (must fail, payload binding is mandatory)
    stripped_packet = {k: v for k, v in proof_packet.items() if k != "canonical_payload"}
    assert EvidenceStore.verify_merkle_proof(stripped_packet) is False

    # 5. Empty canonical_payload (must fail)
    empty_payload_packet = dict(proof_packet)
    empty_payload_packet["canonical_payload"] = ""
    assert EvidenceStore.verify_merkle_proof(empty_payload_packet) is False

