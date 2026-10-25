"""
Azure IoT Hub / Event Hubs consumer client listener.
Listens asynchronously for telemetry events, decodes them via converter,
and dispatches normalized telemetry objects to the server state.
"""

import time
import threading
from typing import Callable, Optional
from datetime import datetime, timezone

try:
    from azure.eventhub import EventHubConsumerClient
except ImportError:
    EventHubConsumerClient = None


class AzureReceiver:
    def __init__(
        self,
        connection_string: Optional[str],
        consumer_group: str = "$default",
        dispatch_fn: Optional[Callable[[any, str, Optional[datetime]], None]] = None,
        on_status_change: Optional[Callable[[str, Optional[str]], None]] = None,
    ):
        self.connection_string = connection_string
        self.consumer_group = consumer_group or "$default"
        self.dispatch_fn = dispatch_fn
        self.on_status_change = on_status_change
        self.status = "DISCONNECTED"
        self.last_error = None
        self._running = False
        self._thread = None
        self._client = None

    def _set_status(self, status: str, error: Optional[str] = None):
        self.status = status
        self.last_error = error
        if self.on_status_change:
            try:
                self.on_status_change(status, error)
            except Exception as e:
                print(f"[AzureReceiver] Status callback error: {e}", flush=True)

    def is_configured(self) -> bool:
        if not self.connection_string:
            return False
        clean = self.connection_string.strip()
        # Ensure it's not a placeholder
        if "your endpoint" in clean or "your shared access key" in clean or clean == "":
            return False
        return "Endpoint=" in clean

    def start(self):
        if not self.is_configured():
            self._set_status("DISCONNECTED", "Azure connection string not configured or contains placeholder.")
            print("[AzureReceiver] Azure connection string not configured. Standing by.", flush=True)
            return

        if EventHubConsumerClient is None:
            self._set_status("ERROR", "azure-eventhub library is not installed.")
            return

        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True, name="AzureReceiverThread")
        self._thread.start()

    def stop(self):
        self._running = False
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass

    def _run(self):
        backoff = 2
        while self._running:
            try:
                self._set_status("CONNECTING", None)
                print(f"[AzureReceiver] Connecting to Azure Event Hub (Consumer Group: {self.consumer_group})...", flush=True)

                self._client = EventHubConsumerClient.from_connection_string(
                    conn_str=self.connection_string,
                    consumer_group=self.consumer_group,
                )

                def on_event(partition_context, event):
                    if not self._running or event is None:
                        return

                    # Update status to CONNECTED upon first event arrival or partition connection
                    if self.status != "CONNECTED":
                        self._set_status("CONNECTED", None)

                    raw_body = event.body_as_str(encoding="UTF-8")
                    enqueued_time = event.enqueued_time
                    if self.dispatch_fn:
                        self.dispatch_fn(raw_body, "azure", enqueued_time)

                def on_error(partition_context, error):
                    print(f"[AzureReceiver] Partition error: {error}", flush=True)
                    self._set_status("ERROR", str(error))

                with self._client:
                    # Successful connect
                    self._set_status("CONNECTED", None)
                    print("[AzureReceiver] Connected and listening for Azure telemetry events starting at @latest...", flush=True)
                    self._client.receive(
                        on_event=on_event,
                        on_error=on_error,
                        starting_position="@latest",
                    )

            except Exception as exc:
                err_msg = str(exc)
                print(f"[AzureReceiver] Connection error: {err_msg}", flush=True)
                self._set_status("ERROR", err_msg)
                if not self._running:
                    break
                time.sleep(backoff)
                backoff = min(backoff * 2, 60)
