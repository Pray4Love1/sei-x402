// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IGuardianOracle {
    function isSessionApproved(address identity) external view returns (bool);
}

contract OmegaHooks {
    IGuardianOracle public guardian;
    address public immutable identity;

    constructor(address _oracle, address _identity) {
        guardian = IGuardianOracle(_oracle);
        identity = _identity;
    }

    modifier guarded() {
        require(guardian.isSessionApproved(identity), "Guardian rejection");
        _;
    }

    function performProtectedAction() external guarded {
        // Protected function
    }
}
