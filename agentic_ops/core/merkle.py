"""
agentic_ops/core/merkle.py
Mathematical & Cryptographic Binary Merkle Tree implementation adhering to RFC 6962.
Provides:
- Strict canonical leaf hashing with 0x00 domain separator (second-preimage resistance).
- Pairwise internal node hashing with 0x01 domain separator.
- Root hash computation over batches of episodes.
- O(log N) Audit Proof (Proof of Inclusion) generation.
- O(log N) Audit Proof verification without access to the full ledger.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional, Union


def hash_leaf(data: Union[bytes, str, Dict[str, Any]]) -> str:
    """
    Computes RFC 6962 leaf hash: SHA-256(0x00 || canonical_bytes).
    The 0x00 prefix prevents second-preimage attacks where an internal node
    could be substituted for a leaf.
    """
    if isinstance(data, dict):
        raw = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    elif isinstance(data, str):
        raw = data.encode("utf-8")
    elif isinstance(data, bytes):
        raw = data
    else:
        raw = str(data).encode("utf-8")
    return hashlib.sha256(b"\x00" + raw).hexdigest()


def hash_children(left_hex: str, right_hex: str) -> str:
    """
    Computes RFC 6962 internal node hash: SHA-256(0x01 || left_bytes || right_bytes).
    The 0x01 prefix ensures internal node hashes can never collide with leaf hashes.
    """
    left_bytes = bytes.fromhex(left_hex)
    right_bytes = bytes.fromhex(right_hex)
    return hashlib.sha256(b"\x01" + left_bytes + right_bytes).hexdigest()


class MerkleTree:
    """
    Binary Merkle Tree representing an immutable batch of evidence/episodes.
    """

    def __init__(self, leaves: Optional[List[Union[str, bytes, Dict[str, Any]]]] = None):
        self.raw_leaves: List[Any] = leaves or []
        self.leaf_hashes: List[str] = [
            leaf if isinstance(leaf, str) and len(leaf) == 64 and all(c in "0123456789abcdefABCDEF" for c in leaf)
            else hash_leaf(leaf)
            for leaf in self.raw_leaves
        ]
        self.levels: List[List[str]] = []
        self._build_tree()

    def _build_tree(self) -> None:
        """Constructs all levels of the tree from bottom to root."""
        if not self.leaf_hashes:
            # Empty tree root is SHA-256 of empty string
            self.levels = [[hashlib.sha256(b"").hexdigest()]]
            return

        current_level = list(self.leaf_hashes)
        self.levels = [current_level]

        while len(current_level) > 1:
            next_level: List[str] = []
            n = len(current_level)
            for i in range(0, n, 2):
                left = current_level[i]
                if i + 1 < n:
                    right = current_level[i + 1]
                else:
                    # Odd number of nodes: RFC 6962 standard duplicates the lone node
                    right = left
                parent = hash_children(left, right)
                next_level.append(parent)
            self.levels.append(next_level)
            current_level = next_level

    @property
    def root(self) -> str:
        """Returns the 32-byte hex Merkle Root."""
        if not self.levels or not self.levels[-1]:
            return hashlib.sha256(b"").hexdigest()
        return self.levels[-1][0]

    def get_root(self) -> str:
        return self.root

    def get_audit_proof(self, leaf_index: int) -> List[Dict[str, str]]:
        """
        Generates an O(log N) audit proof of inclusion for the leaf at `leaf_index`.
        Returns a list of sibling steps:
        [
            {"position": "left" | "right", "hash": "hex..."},
            ...
        ]
        """
        if leaf_index < 0 or leaf_index >= len(self.leaf_hashes):
            raise IndexError(f"Leaf index {leaf_index} out of bounds (total leaves: {len(self.leaf_hashes)})")

        proof: List[Dict[str, str]] = []
        idx = leaf_index

        for level in self.levels[:-1]:
            level_len = len(level)
            if idx % 2 == 0:
                # Left child -> sibling is on the right
                if idx + 1 < level_len:
                    sibling = level[idx + 1]
                else:
                    # Lone child duplicated itself
                    sibling = level[idx]
                proof.append({"position": "right", "hash": sibling})
            else:
                # Right child -> sibling is on the left
                sibling = level[idx - 1]
                proof.append({"position": "left", "hash": sibling})

            idx //= 2

        return proof

    @staticmethod
    def verify_audit_proof(
        leaf: Union[str, bytes, Dict[str, Any]],
        proof: List[Dict[str, str]],
        expected_root: str,
    ) -> bool:
        """
        Verifies that `leaf` belongs to the tree with `expected_root` using `proof`.
        Execution time is O(log N), completely independent of total ledger size.
        """
        if isinstance(leaf, str) and len(leaf) == 64 and all(c in "0123456789abcdefABCDEF" for c in leaf):
            curr = leaf.lower()
        else:
            curr = hash_leaf(leaf).lower()

        expected = expected_root.lower()

        for step in proof:
            pos = step.get("position")
            sibling = str(step.get("hash", "")).lower()
            if pos == "left":
                curr = hash_children(sibling, curr)
            elif pos == "right":
                curr = hash_children(curr, sibling)
            else:
                return False

        return curr.lower() == expected
