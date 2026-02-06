// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title CodexDropVerifier - Validates a CodexDrop hash for royalty enforcement
contract CodexDropVerifier {
    /// @dev Hardcoded Codex drop hash (per chain)
    bytes32 public immutable CODEX_DROP_HASH;

    constructor(bytes32 dropHash) {
        CODEX_DROP_HASH = dropHash;
    }

    /// @notice Verifies input hash matches the sealed Codex drop
    function verify(bytes32 inputHash) external view returns (bool) {
        return inputHash == CODEX_DROP_HASH;
    }

    /// @notice Throws if input hash is invalid
    function requireMatch(bytes32 inputHash) external view {
        require(inputHash == CODEX_DROP_HASH, "Codex hash mismatch");
    }
}
