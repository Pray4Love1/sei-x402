// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VaultReplayBlocker {
    mapping(bytes32 => bool) public used;

    function checkAndMark(bytes32 hash) external returns (bool) {
        require(!used[hash], "Replay detected");
        used[hash] = true;
        return true;
    }
}
