#!/bin/bash
set -euo pipefail

echo "Deploying ReceivingVault via forge..."
forge script forge.deploy.ts --broadcast --rpc-url "$RPC_URL"
