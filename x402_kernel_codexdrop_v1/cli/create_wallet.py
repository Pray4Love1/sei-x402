import json

from lib.entropy_utils import derive_root_seed, generate_entropy, generate_mnemonic
from lib.wallet_deriver import get_receive_address

username = input("Username: ")
pin = input("PIN (CipherWord): ")
guardians = input("Guardians (comma-separated): ").split(",")
salt = input("Entropy Salt: ")

entropy = generate_entropy(username, pin, guardians, salt)
mnemonic = generate_mnemonic(entropy)
seed = derive_root_seed(mnemonic)
receive_address = get_receive_address(seed)

wallet = {
    "handle": f"@{username}",
    "mnemonic": mnemonic,
    "receiveAddress": receive_address,
    "spendIndex": 0,
    "guardians": guardians,
    "salt": salt,
    "agent": "CodexSig",
}

with open("wallet_state.json", "w", encoding="utf-8") as handle:
    json.dump(wallet, handle, indent=2)

print(f"✅ Wallet created. Receive address: {receive_address}")
