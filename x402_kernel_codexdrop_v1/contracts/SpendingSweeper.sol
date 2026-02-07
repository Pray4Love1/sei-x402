// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IVault {
    function rotateSweeper(address _newSweeper) external;
}

contract SpendingSweeper {
    address public vault;
    address public owner;

    constructor(address _vault) {
        vault = _vault;
        owner = msg.sender;
    }

    function spendAndRotate(address payable to, address nextSweeper) external {
        require(msg.sender == owner, "Not authorized");

        (bool sent, ) = to.call{value: address(this).balance}("");
        require(sent, "TX failed");

        IVault(vault).rotateSweeper(nextSweeper);
    }

    receive() external payable {}
}
