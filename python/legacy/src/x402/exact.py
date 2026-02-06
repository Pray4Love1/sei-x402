import time
import secrets
import json
from typing import Dict, Any
from typing_extensions import TypedDict  # Python <3.12 support

from eth_account import Account
from hexbytes import HexBytes

from x402.encoding import safe_base64_encode, safe_base64_decode
from x402.types import PaymentRequirements
from x402.chains import get_chain_id


# -----------------------------
# Nonce helpers (canonical)
# -----------------------------

def create_nonce_hex() -> str:
    """
    Create a canonical 32-byte nonce encoded as a hex string (0x-prefixed).

    This is the ONLY format emitted at the public API boundary.
    """
    return f"0x{secrets.token_bytes(32).hex()}"


# -----------------------------
# Header construction
# -----------------------------

def prepare_payment_header(
    sender_address: str,
    x402_version: int,
    payment_requirements: PaymentRequirements,
) -> Dict[str, Any]:
    """
    Prepare an unsigned payment header.

    Canonical rules:
    - nonce is ALWAYS a hex string
    - timestamps are unix seconds (stringified)
    """
    nonce_hex = create_nonce_hex()
    now = int(time.time())

    valid_after = str(now - 60)  # allow slight clock skew
    valid_before = str(now + payment_requirements.max_timeout_seconds)

    return {
        "x402Version": x402_version,
        "scheme": payment_requirements.scheme,
        "network": payment_requirements.network,
        "payload": {
            "signature": None,
            "authorization": {
                "from": sender_address,
                "to": payment_requirements.pay_to,
                "value": payment_requirements.max_amount_required,
                "validAfter": valid_after,
                "validBefore": valid_before,
                "nonce": nonce_hex,
            },
        },
    }


class PaymentHeader(TypedDict):
    x402Version: int
    scheme: str
    network: str
    payload: Dict[str, Any]


# -----------------------------
# Signing
# -----------------------------

def sign_payment_header(
    account: Account,
    payment_requirements: PaymentRequirements,
    header: PaymentHeader,
) -> str:
    """
    Sign a payment header using EIP-712 TransferWithAuthorization.

    Canonical rule:
    - nonce MUST be hex string at rest
    - bytes are accepted defensively
    """
    auth = header["payload"]["authorization"]
    auth_nonce = auth["nonce"]

    # --- Normalize nonce ---
    if isinstance(auth_nonce, (bytes, bytearray)):
        nonce_bytes = bytes(auth_nonce)
        nonce_hex = f"0x{nonce_bytes.hex()}"
    elif isinstance(auth_nonce, str):
        nonce_hex = auth_nonce if auth_nonce.startswith("0x") else f"0x{auth_nonce}"
        nonce_bytes = bytes.fromhex(nonce_hex[2:])
    else:
        raise TypeError("Authorization nonce must be bytes or hex string")

    typed_data = {
        "types": {
            "TransferWithAuthorization": [
                {"name": "from", "type": "address"},
                {"name": "to", "type": "address"},
                {"name": "value", "type": "uint256"},
                {"name": "validAfter", "type": "uint256"},
                {"name": "validBefore", "type": "uint256"},
                {"name": "nonce", "type": "bytes32"},
            ]
        },
        "primaryType": "TransferWithAuthorization",
        "domain": {
            "name": payment_requirements.extra["name"],
            "version": payment_requirements.extra["version"],
            "chainId": int(get_chain_id(payment_requirements.network)),
            "verifyingContract": payment_requirements.asset,
        },
        "message": {
            "from": auth["from"],
            "to": auth["to"],
            "value": int(auth["value"]),
            "validAfter": int(auth["validAfter"]),
            "validBefore": int(auth["validBefore"]),
            "nonce": nonce_bytes,
        },
    }

    signed = account.sign_typed_data(
        domain_data=typed_data["domain"],
        message_types=typed_data["types"],
        message_data=typed_data["message"],
    )

    signature = signed.signature.hex()
    if not signature.startswith("0x"):
        signature = f"0x{signature}"

    header["payload"]["signature"] = signature

    # Re‑emit nonce in canonical form
    header["payload"]["authorization"]["nonce"] = nonce_hex

    return encode_payment(header)


# -----------------------------
# Encoding / decoding
# -----------------------------

def encode_payment(payment_payload: Dict[str, Any]) -> str:
    """
    Encode a payment payload into URL-safe base64 JSON.
    """

    def default(obj):
        if isinstance(obj, HexBytes):
            return obj.hex()
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        if hasattr(obj, "hex"):
            return obj.hex()
        raise TypeError(
            f"Object of type {obj.__class__.__name__} is not JSON serializable"
        )

    return safe_base64_encode(json.dumps(payment_payload, default=default))


def decode_payment(encoded_payment: str) -> Dict[str, Any]:
    """
    Decode a base64 encoded payment payload.
    """
    return json.loads(safe_base64_decode(encoded_payment))
