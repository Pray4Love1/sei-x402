// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title CodexDropRegistry - Multi-chain hash registry for CodexDrop validation
contract CodexDropRegistry {
    address public owner;
    mapping(uint256 => bytes32) public dropHashByChain;

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function setDropHash(uint256 chainId, bytes32 dropHash) external onlyOwner {
        dropHashByChain[chainId] = dropHash;
    }

    function getDropHash(uint256 chainId) external view returns (bytes32) {
        return dropHashByChain[chainId];
    }

    function verifyHash(uint256 chainId, bytes32 inputHash) external view returns (bool) {
        return dropHashByChain[chainId] == inputHash;
    }

    function requireMatch(uint256 chainId, bytes32 inputHash) external view {
        require(dropHashByChain[chainId] == inputHash, "Hash mismatch for chain");
    }
}
