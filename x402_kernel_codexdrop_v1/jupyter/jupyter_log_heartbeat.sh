#!/bin/bash
set -euo pipefail

TS=$(date +"%Y-%m-%dT%H:%M:%S")
ADDR=$(jq -r .receiveAddress wallet_state.json)
ENTROPY=$(jq -r .mnemonic wallet_state.json | sha256sum | cut -d' ' -f1)

echo "$TS | $ADDR | $ENTROPY" >> jupyter/state_log.ipynb
