import time


class TransientAPIError(Exception):
    pass


class FlakyAPI:
    """Simulates a real API that fails on its first few calls (a transient
    blip - a brief outage, a cold cache, a rate limit that clears) and then
    recovers. Fails deterministically so the proof is reproducible, not
    dependent on random chance."""

    def __init__(self, fail_until_call=4):
        self.fail_until_call = fail_until_call
        self.call_count = 0
        self.call_log = []

    def call(self):
        self.call_count += 1
        timestamp = time.monotonic()
        if self.call_count <= self.fail_until_call:
            self.call_log.append((self.call_count, timestamp, "FAILED"))
            raise TransientAPIError(
                f"call #{self.call_count}: simulated transient failure"
            )
        self.call_log.append((self.call_count, timestamp, "SUCCESS"))
        return {"status": "ok", "call_number": self.call_count}
