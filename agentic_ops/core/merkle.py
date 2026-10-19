"""
agentic_ops/core/merkle.py
Mathematical & Cryptographic Binary Merkle Tree implementation strictly adhering to RFC 6962
(Certificate Transparency - Merkle Tree Hash & Audit Paths).

RFC 6962 Section 2.1 Specification:
- MTH({}) = SHA-256("")
- MTH({d(0)}) = SHA-256(0x00 || d(0))
- For n > 1: let k be the largest power of two smaller than n (k < n <= 2k).
  MTH(D[n]) = SHA-256(0x01 || MTH(D[0:k]) || MTH(D[k:n]))

RFC 6962 Section 2.1.1 Specification (Audit Paths):
- PATH(0, {d(0)}) = {}
- For n > 1, let k be the largest power of two smaller than n:
  PATH(m, D[n]) = PATH(m, D[0:k]) : MTH(D[k:n])  for m < k
  PATH(m, D[n]) = PATH(m - k, D[k:n]) : MTH(D[0:k]) for m >= k

Complexity Profile:
- Tree Construction / MTH computation: O(N) time and memory.
- Audit Proof Generation: O(N) traversal over unindexed leaf sequence.
- Audit Proof Size: O(log N) hashes (at most ceil(log2 N) siblings).
- Audit Proof Verification: O(log N) hash operations, independent of total ledger size.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional, Sequence, Union


def hash_leaf(data: Union[bytes, str, Dict[str, Any]]) -> str:
    """
    Computes RFC 6962 leaf hash: SHA-256(0x00 || canonical_bytes).
    The 0x00 prefix enforces domain separation, preventing second-preimage attacks.
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


def largest_power_of_two_less_than(n: int) -> int:
    """
    Returns the largest power of two strictly smaller than n (i.e. k < n <= 2k),
    per RFC 6962 Section 2.1.
    """
    if n <= 1:
        return 0
    k = 1
    while k * 2 < n:
        k *= 2
    return k


def compute_rfc6962_mth(
    leaf_hashes: Sequence[str],
    start: int = 0,
    end: Optional[int] = None,
) -> str:
    """
    Computes RFC 6962 Merkle Tree Hash (MTH) recursively in O(N) time and O(log N) stack depth:
    - MTH({}) = SHA-256("")
    - MTH({d_0}) = leaf_hash
    - For n > 1: k = largest power of two < n
      MTH(D[n]) = SHA-256(0x01 || MTH(D[0:k]) || MTH(D[k:n]))

    Operates on index bounds [start:end] to avoid list slicing allocations.
    """
    if end is None:
        end = len(leaf_hashes)
    n = end - start
    if n == 0:
        return hashlib.sha256(b"").hexdigest()
    if n == 1:
        return leaf_hashes[start]
    k = largest_power_of_two_less_than(n)
    left_mth = compute_rfc6962_mth(leaf_hashes, start, start + k)
    right_mth = compute_rfc6962_mth(leaf_hashes, start + k, end)
    return hash_children(left_mth, right_mth)


def compute_rfc6962_audit_path(
    m: int,
    leaf_hashes: Sequence[str],
    start: int = 0,
    end: Optional[int] = None,
) -> List[Dict[str, str]]:
    """
    Computes RFC 6962 Section 2.1.1 audit path for leaf at index m:
    - If n <= 1: empty path
    - For n > 1:
      If m < k: recursive path in D[0:k] with sibling MTH(D[k:n]) on the right
      If m >= k: recursive path in D[k:n] with sibling MTH(D[0:k]) on the left

    Operates on index bounds [start:end] to avoid list slicing allocations.
    """
    if end is None:
        end = len(leaf_hashes)
    n = end - start
    if n <= 1:
        return []
    if m < 0 or m >= n:
        raise IndexError(f"Leaf index {m} out of bounds (total leaves: {n})")
    k = largest_power_of_two_less_than(n)
    if m < k:
        right_sibling = compute_rfc6962_mth(leaf_hashes, start + k, end)
        return compute_rfc6962_audit_path(m, leaf_hashes, start, start + k) + [{"position": "right", "hash": right_sibling}]
    else:
        left_sibling = compute_rfc6962_mth(leaf_hashes, start, start + k)
        return compute_rfc6962_audit_path(m - k, leaf_hashes, start + k, end) + [{"position": "left", "hash": left_sibling}]


class MerkleTree:
    """
    Strict RFC 6962 Binary Merkle Tree implementation.
    
    Complexity Profile:
    - Tree Construction / MTH computation: O(N) time and memory.
    - Audit Proof Generation: O(N) traversal over unindexed leaf sequence.
    - Audit Proof Size: O(log N) hashes (at most ceil(log2 N) siblings).
    - Audit Proof Verification: O(log N) hash operations, independent of total ledger size.
    """

    def __init__(self, leaves: Optional[List[Union[str, bytes, Dict[str, Any]]]] = None):
        self.raw_leaves: List[Any] = leaves or []
        self.leaf_hashes: List[str] = [
            leaf if isinstance(leaf, str) and len(leaf) == 64 and all(c in "0123456789abcdefABCDEF" for c in leaf)
            else hash_leaf(leaf)
            for leaf in self.raw_leaves
        ]
        self._root: Optional[str] = None

    @property
    def root(self) -> str:
        """Returns the 32-byte hex Merkle Root (RFC 6962 MTH)."""
        if self._root is None:
            self._root = compute_rfc6962_mth(self.leaf_hashes)
        return self._root

    def get_root(self) -> str:
        return self.root

    def get_audit_proof(self, leaf_index: int) -> List[Dict[str, str]]:
        """
        Generates the RFC 6962 Section 2.1.1 audit path of inclusion for the leaf at `leaf_index`.
        Returns a list of sibling steps ordered from leaf level to root:
        [
            {"position": "left" | "right", "hash": "hex..."},
            ...
        ]
        """
        return compute_rfc6962_audit_path(leaf_index, self.leaf_hashes)

    @staticmethod
    def verify_audit_proof(
        leaf: Union[str, bytes, Dict[str, Any]],
        proof: List[Dict[str, str]],
        expected_root: str,
    ) -> bool:
        """
        Verifies that `leaf` belongs to the tree with `expected_root` using `proof`.
        Execution time is strictly O(log N), completely independent of total ledger size.
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
