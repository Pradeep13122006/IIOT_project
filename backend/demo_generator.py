"""
Demo telemetry generator for local testing and evaluation when live Azure
credentials are not yet configured. Emits simulated IoT messages with ASCII payloads.
"""

import time
import threading
from typing import Callable

DEMO_MESSAGES = [
    "72,101,108,108,111",                               # Hello
    "65,122,117,114,101,32,73,111,84",                 # Azure IoT
    "84,101,108,101,109,101,116,114,121,32,79,75",     # Telemetry OK
    "83,116,117,100,101,110,116,32,80,114,111,106,101,99,116", # Student Project
    "83,101,110,115,111,114,32,65,99,116,105,118,101", # Sensor Active
    "67,111,110,110,101,99,116,101,100",               # Connected
]


class DemoGenerator:
    def __init__(self, dispatch_fn: Callable[[str, str], None], interval_seconds: float = 3.0):
        self.dispatch_fn = dispatch_fn
        self.interval = interval_seconds
        self._running = False
        self._thread = None
        self._index = 0

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True, name="DemoGeneratorThread")
        self._thread.start()

    def stop(self):
        self._running = False

    def _run(self):
        while self._running:
            payload = DEMO_MESSAGES[self._index % len(DEMO_MESSAGES)]
            self._index += 1
            try:
                self.dispatch_fn(payload, "demo")
            except Exception as e:
                print(f"[DemoGenerator] Error dispatching payload: {e}", flush=True)
            time.sleep(self.interval)
