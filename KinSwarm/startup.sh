#!/usr/bin/env bash
set -euo pipefail

./KinSwarm/setup.sh

if [ ! -f KinSwarm/offline/operator.key ]; then
  echo "bootstrap-local-signer-key" > KinSwarm/offline/operator.key
fi

python -m KinSwarm.swarm_manager
