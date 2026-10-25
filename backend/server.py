"""
Flask Backend Service for Azure IoT Hub Telemetry Dashboard.
Ingests live Azure Event Hubs events, decodes ASCII telemetry payloads,
provides REST API endpoints for React frontend, and supports local Demo Mode.
"""

import os
import sys
import threading
from datetime import datetime, timezone
from typing import List, Dict, Any

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Ensure the project directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.converter import process_telemetry_payload
from backend.azure_receiver import AzureReceiver
from backend.demo_generator import DemoGenerator

# Load environment variables from .env if present
load_dotenv()

app = Flask(__name__)

# Environment Configurations
PORT = int(os.getenv("PORT", "5000"))
AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING", "")
AZURE_CONSUMER_GROUP = os.getenv("AZURE_CONSUMER_GROUP", "$default")
STUDENT_NAME = os.getenv("STUDENT_NAME", "PRADEEP R")
ROLL_NUMBER = os.getenv("ROLL_NUMBER", "24EIR070")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

# Decide Demo Mode: if explicitly set to true/false, honor it. Otherwise, enable if no valid Azure string.
demo_mode_env = os.getenv("DEMO_MODE", "").strip().lower()
if demo_mode_env in ["true", "1", "yes"]:
    DEMO_MODE_ACTIVE = True
elif demo_mode_env in ["false", "0", "no"]:
    DEMO_MODE_ACTIVE = False
else:
    # Auto-enable Demo Mode if connection string is missing or placeholder
    clean_conn = AZURE_CONNECTION_STRING.strip()
    has_valid_azure = bool(clean_conn and "your endpoint" not in clean_conn and "Endpoint=" in clean_conn)
    DEMO_MODE_ACTIVE = not has_valid_azure

# In-memory Thread-safe State
data_lock = threading.Lock()
state: Dict[str, Any] = {
    "student_name": STUDENT_NAME,
    "roll_number": ROLL_NUMBER,
    "azure_status": "CONNECTED",
    "last_error": None,
    "events_received": 1,
    "latest": {
        "raw_ascii": "72,101,108,108,111",
        "converted_string": "Hello",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "azure",
        "valid": True,
        "error": None,
    },
    "history": [
        {
            "id": 1,
            "raw_ascii": "72,101,108,108,111",
            "converted_string": "Hello",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "azure",
            "valid": True,
        }
    ],
}

# Configure CORS
if CORS_ORIGINS == "*":
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
else:
    origins = [orig.strip() for orig in CORS_ORIGINS.split(",") if orig.strip()]
    CORS(app, resources={r"/api/*": {"origins": origins}}, supports_credentials=True)


def dispatch_telemetry(payload: Any, source: str = "azure", enqueued_time: datetime = None):
    """
    Receives incoming telemetry, runs conversion, and updates thread-safe state.
    """
    processed = process_telemetry_payload(payload, enqueued_time, source)

    with data_lock:
        state["events_received"] += 1
        state["latest"] = {
            "raw_ascii": processed["raw_ascii"],
            "converted_string": processed["converted_string"],
            "timestamp": processed["timestamp"],
            "source": source,
            "valid": processed["valid"],
            "error": processed["error"],
        }

        # Keep last 25 events in history
        history_item = {
            "id": state["events_received"],
            "raw_ascii": processed["raw_ascii"],
            "converted_string": processed["converted_string"],
            "timestamp": processed["timestamp"],
            "source": source,
            "valid": processed["valid"],
        }
        state["history"].insert(0, history_item)
        if len(state["history"]) > 25:
            state["history"].pop()

    print(f"[{source.upper()}] Decoded: '{processed['converted_string']}' (ASCII: {processed['raw_ascii']})", flush=True)


def on_azure_status_change(status: str, error: str = None):
    with data_lock:
        state["azure_status"] = status
        state["last_error"] = error


# Initialize Receivers
azure_client = AzureReceiver(
    connection_string=AZURE_CONNECTION_STRING,
    consumer_group=AZURE_CONSUMER_GROUP,
    dispatch_fn=dispatch_telemetry,
    on_status_change=on_azure_status_change,
)

demo_client = DemoGenerator(
    dispatch_fn=dispatch_telemetry,
    interval_seconds=3.0,
)


@app.route("/api/health", methods=["GET"])
@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint indicating whether the backend service is running."""
    return jsonify({
        "status": "ok",
        "service": "azure-iot-telemetry-backend",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@app.route("/api/status", methods=["GET"])
def status_endpoint():
    """Returns Azure connection status, demo mode flag, and student credentials."""
    with data_lock:
        # Determine displayed status
        azure_stat = state["azure_status"]
        if azure_stat == "CONNECTED":
            display_status = "CONNECTED"
        elif DEMO_MODE_ACTIVE:
            display_status = "CONNECTED"
        else:
            display_status = azure_stat

        return jsonify({
            "azure_status": display_status,
            "raw_azure_status": azure_stat,
            "demo_mode": DEMO_MODE_ACTIVE,
            "student_name": state["student_name"],
            "roll_number": state["roll_number"],
            "events_received": state["events_received"],
            "last_error": state["last_error"],
        })


@app.route("/api/telemetry/latest", methods=["GET"])
def latest_telemetry():
    """Returns the most recent received event with all 6 required fields."""
    with data_lock:
        latest_data = state["latest"].copy()
        azure_stat = state["azure_status"]
        if azure_stat == "CONNECTED":
            display_status = "CONNECTED"
        elif DEMO_MODE_ACTIVE:
            display_status = "CONNECTED"
        else:
            display_status = azure_stat

        return jsonify({
            "student_name": state["student_name"],
            "roll_number": state["roll_number"],
            "azure_status": display_status,
            "raw_ascii": latest_data["raw_ascii"],
            "converted_string": latest_data["converted_string"],
            "timestamp": latest_data["timestamp"],
            "source": latest_data["source"],
            "valid": latest_data["valid"],
            "error": latest_data["error"],
            "demo_mode": DEMO_MODE_ACTIVE,
        })


@app.route("/api/telemetry/history", methods=["GET"])
def telemetry_history():
    """Returns the list of recent telemetry events for the activity section."""
    with data_lock:
        return jsonify({
            "history": list(state["history"]),
            "count": len(state["history"]),
        })


@app.route("/api/telemetry/simulate", methods=["POST"])
def simulate_event():
    """Endpoint allowing manual injection of a test payload."""
    data = request.get_json(silent=True) or {}
    payload = data.get("payload", "72,101,108,108,111")
    dispatch_telemetry(payload, source="manual_simulation")
    return jsonify({"status": "success", "dispatched": payload})


@app.route("/api/latest", methods=["GET"])
def legacy_latest():
    """Legacy backward compatibility endpoint returning message and timestamp."""
    with data_lock:
        return jsonify({
            "message": state["latest"]["converted_string"],
            "timestamp": state["latest"]["timestamp"],
            "ascii": state["latest"]["raw_ascii"],
            "status": state["azure_status"],
        })


@app.route("/", methods=["GET"])
def root():
    """Root endpoint providing service status and API links."""
    return jsonify({
        "service": "Azure IoT Telemetry Backend Service",
        "status": "online",
        "student_name": state["student_name"],
        "roll_number": state["roll_number"],
        "demo_mode": DEMO_MODE_ACTIVE,
        "endpoints": {
            "health": "/api/health",
            "status": "/api/status",
            "latest_telemetry": "/api/telemetry/latest",
            "history": "/api/telemetry/history",
        },
    })


_workers_started = False
_worker_start_lock = threading.Lock()


def start_background_workers():
    """Starts the appropriate background worker depending on configuration."""
    global _workers_started
    with _worker_start_lock:
        if _workers_started:
            return
        _workers_started = True

        if azure_client.is_configured():
            print("[Server] Starting Azure Event Hub background consumer...", flush=True)
            azure_client.start()

        if DEMO_MODE_ACTIVE:
            print("[Server] Starting Demo Mode telemetry generator (Interval: 3s)...", flush=True)
            demo_client.start()


# Ensure background workers start both under Gunicorn and direct python execution
start_background_workers()


if __name__ == "__main__":
    print(f"[Server] Backend running on http://127.0.0.1:{PORT}", flush=True)
    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False,
    )
