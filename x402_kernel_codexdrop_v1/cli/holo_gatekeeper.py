"""Local biometric + mood checks."""

from __future__ import annotations


def validate_mood(mood_level: int, biometric_score: int) -> None:
    if mood_level < 70:
        raise ValueError("Mood check failed")
    if biometric_score < 85:
        raise ValueError("Biometric score too low")
    print("✅ Holo gate passed")


if __name__ == "__main__":
    validate_mood(mood_level=80, biometric_score=90)
