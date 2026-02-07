import json

with open("wallet_state.json", encoding="utf-8") as handle:
    wallet = json.load(handle)

wallet["spendIndex"] += 1

with open("wallet_state.json", "w", encoding="utf-8") as handle:
    json.dump(wallet, handle, indent=2)

print(f"🔁 Rotated to session key index {wallet['spendIndex']}")
