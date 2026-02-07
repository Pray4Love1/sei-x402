import json

from web3 import Web3

from lib.entropy_utils import derive_root_seed
from lib.sovereign_signer import SovereignSigner

with open("wallet_state.json", encoding="utf-8") as handle:
    wallet = json.load(handle)

seed = derive_root_seed(wallet["mnemonic"])
signer = SovereignSigner(seed, wallet["agent"])
index = wallet["spendIndex"]

tx = {
    "to": Web3.to_checksum_address("0xAbC...dead"),
    "value": Web3.to_wei(0.01, "ether"),
    "nonce": 0,  # Replace with w3.eth.get_transaction_count()
    "gas": 21000,
    "gasPrice": Web3.to_wei(30, "gwei"),
}

raw = signer.sign(tx, index)
print("Signed TX:", raw.hex())
