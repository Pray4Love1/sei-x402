// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VaultHooks {
    mapping(address => bool) public authorized;
    address public omegaGuardian;

    constructor(address _omegaGuardian) {
        omegaGuardian = _omegaGuardian;
    }

    modifier onlyOmega() {
        require(msg.sender == omegaGuardian, "Not Omega Guardian");
        _;
    }

    function authorize(address session) external onlyOmega {
        authorized[session] = true;
    }

    function revoke(address session) external onlyOmega {
        authorized[session] = false;
    }

    function protectedSweep(address payable _to) external {
        require(authorized[msg.sender], "Session not authorized");
        _to.transfer(address(this).balance);
    }

    receive() external payable {}
}
