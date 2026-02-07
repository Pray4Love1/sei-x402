import time


def verify_biometrics(mood: int, entropy: int) -> bool:
    if mood < 70 or entropy < 85:
        raise Exception("Guardian lock failed")
    with open("guardian_heartbeat.log", "a", encoding="utf-8") as handle:
        handle.write(f"{time.time()} | OK\n")
    return True
