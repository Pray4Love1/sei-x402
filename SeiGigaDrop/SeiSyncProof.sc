// SeiSyncProof.sc - reference contract for sealed proof registration
// Rename to .sol for Solidity tooling.

pragma solidity ^0.8.20;

contract SeiSyncProof {
    event ProofRegistered(bytes32 indexed digest, address indexed signer, uint256 timestamp);

    mapping(bytes32 => address) public registeredBy;

    function registerProof(bytes32 digest) external {
        require(digest != bytes32(0), "digest required");
        require(registeredBy[digest] == address(0), "digest already registered");
        registeredBy[digest] = msg.sender;
        emit ProofRegistered(digest, msg.sender, block.timestamp);
    }
}
