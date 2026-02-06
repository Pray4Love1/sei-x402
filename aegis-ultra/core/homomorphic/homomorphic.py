from typing import Iterable


def encrypt_value(value: float) -> str:
    return f"enc:{value}"


def decrypt_value(ciphertext: str) -> float:
    return float(ciphertext.replace("enc:", ""))


def aggregate_encrypted(values: Iterable[str]) -> str:
    total = sum(decrypt_value(value) for value in values)
    return encrypt_value(total)
