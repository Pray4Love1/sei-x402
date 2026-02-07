// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract ReceivingVault {
    address public immutable identity;
    address public spendingSweeper;

    constructor(address _identity, address _sweeper) {
        identity = _identity;
        spendingSweeper = _sweeper;
    }

    receive() external payable {}

    modifier onlySweeper() {
        require(msg.sender == spendingSweeper, "Unauthorized");
        _;
    }

    function sweepTo(address payable _to) external onlySweeper {
        uint256 balance = address(this).balance;
        (bool sent, ) = _to.call{value: balance}("");
        require(sent, "Sweep failed");
    }

    function rotateSweeper(address _newSweeper) external {
        require(msg.sender == identity, "Only identity can rotate");
        spendingSweeper = _newSweeper;
    }
}
