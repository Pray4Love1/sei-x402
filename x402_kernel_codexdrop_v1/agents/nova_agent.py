import requests


class NovaAgent:
    def __init__(self, relay_url: str) -> None:
        self.relay = relay_url

    def submit(self, payload: dict) -> str:
        return requests.post(f"{self.relay}/mcp/proofSubmit", json=payload).text

    def resolve(self, handle: str) -> dict:
        return requests.get(f"{self.relay}/mcp/lookup?handle={handle}").json()
