# Azure IoT Hub Integration & Live Telemetry Dashboard

[![React](https://img.shields.io/badge/React-19.3-blue.svg)](https://react.dev/)
[![Flask](https://img.shields.io/badge/Flask-3.1-black.svg)](https://flask.palletsprojects.com/)
[![Azure IoT](https://img.shields.io/badge/Azure-IoT%20Hub%20%2F%20Event%20Hubs-0078D4.svg)](https://azure.microsoft.com/)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)]()

A full-stack IoT telemetry dashboard engineered to securely ingest, decode, and visualize real-time sensor and device events transmitted from **Azure IoT Hub** / **Azure Event Hubs** using a Python Flask backend and a modern React frontend dashboard.

---

## 📋 Student & Submission Details

| Field | Submission Value |
| :--- | :--- |
| **Student Name** | **PRADEEP R** |
| **Roll Number** | **24EIR070** |
| **Project Name** | Azure IoT Hub Integration & Debugging Dashboard |
| **Repository** | [https://github.com/Pradeep13122006/IIOT_project.git](https://github.com/Pradeep13122006/IIOT_project.git) |
| **Frontend Platform** | Vercel (React SPA) |
| **Backend Service** | Python Flask REST API with Azure EventHub Consumer |

---

## 🎯 Assignment Requirements & Six Mandatory Fields

The dashboard implements and displays all **six fields** explicitly required by the assignment specification:

1. **Student Name**: Displays `PRADEEP R` (configurable via environment variables or backend configuration).
2. **Roll Number**: Displays `24EIR070` (configurable via environment variables or backend configuration).
3. **Azure Connection Status**: Prominent color-coded indicator displaying `CONNECTED`, `CONNECTING`, `DISCONNECTED`, `ERROR`, or `DEMO MODE (SIMULATED)`.
4. **Received ASCII Values**: Raw byte stream or comma-separated ASCII integers (e.g., `72,101,108,108,111`).
5. **Converted String**: Real-time decoded ASCII/UTF-8 string (e.g., `Hello`).
6. **Last Event Timestamp**: Localized readable date and time of the latest received event.

### Conversion Demonstration:
$$\text{Received ASCII Values: } 72, 101, 108, 108, 111 \longrightarrow \text{Converted String: } \mathbf{"Hello"}$$

---

## 🏗️ Architecture & Data Pipeline

```
+--------------------------------------------------------------------------+
|                     IoT Device / Sensor / Simulation                     |
|           Transmits comma-separated ASCII codes or byte arrays           |
+------------------------------------+-------------------------------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
|                              Azure IoT Hub                               |
|                  (Built-in Event Hub-compatible Endpoint)                |
+------------------------------------+-------------------------------------+
                                     |
                                     v (AMQP / EventHubConsumerClient)
+--------------------------------------------------------------------------+
|                       Python Flask Backend Service                       |
|                          (backend/server.py)                             |
|                                                                          |
|   • azure_receiver.py : Background consumer thread (@latest)            |
|   • converter.py      : ASCII validation (0-127), JSON & string parser   |
|   • demo_generator.py : Local simulation mode when Azure is unconfigured |
|   • REST Endpoints    : /api/telemetry/latest, /api/status, /api/health  |
+------------------------------------+-------------------------------------+
                                     |
                                     v (HTTP Polling / Auto-refresh)
+--------------------------------------------------------------------------+
|                          React Frontend Dashboard                        |
|                            (src/azure_web.js)                            |
|                                                                          |
|   • 6 Mandatory Fields Cards (Student Name, Roll No, Status, etc.)       |
|   • ASCII vs Decoded Message Comparison Box                              |
|   • Live Activity History Log Table                                      |
|   • Visual Data Source Pill: 🟢 Live Azure vs 🟡 Demo Mode               |
|   • Manual Reconnect & Immediate Polling Trigger                         |
+--------------------------------------------------------------------------+
```

---

## 📁 Project Structure

```
azure_web/
├── backend/
│   ├── __init__.py           # Package indicator
│   ├── server.py             # Flask application, REST endpoints, CORS & state
│   ├── converter.py          # ASCII decoding engine (0-127 validation & parser)
│   ├── azure_receiver.py     # Azure EventHubConsumerClient background listener
│   ├── demo_generator.py     # Local demo telemetry generator
│   ├── requirements.txt      # Python dependencies
│   └── .env.example          # Backend environment variables template
├── public/                   # Static HTML templates and web manifest
├── src/
│   ├── App.css               # Modern responsive dark theme styling
│   ├── App.js                # React root wrapper
│   ├── App.test.js           # Automated frontend tests
│   ├── azure_web.js          # Core Telemetry Dashboard component
│   ├── index.css             # Base reset styles
│   └── index.js              # React DOM mounting entry point
├── tests/
│   ├── __init__.py           # Tests package init
│   ├── test_api.py           # Unit tests for Flask REST endpoints
│   └── test_converter.py     # Unit tests for ASCII decoding & edge cases
├── .env.example              # Root environment variable template
├── .gitignore                # Comprehensive secret, cache & build exclusion
├── package.json              # React dependencies, testMatch config & scripts
├── requirements.txt          # Root Python dependencies for cloud deployment
├── vercel.json               # Vercel SPA rewrite routing configuration
└── README.md                 # Complete documentation and submission manual
```

---

## ⚙️ Prerequisites

Before getting started, make sure the following runtimes are installed on your system:

- **Node.js**: `v18.0.0` or higher (`v22.x` verified)
- **npm**: `v9.0.0` or higher
- **Python**: `3.9` to `3.11` (`3.11.2` verified)
- **Git**: `2.30` or higher

---

## 🚀 Local Setup Instructions (Windows PowerShell)

Open PowerShell as an Administrator or regular user and navigate to the project directory:

```powershell
Set-Location "C:\Users\PRADEEP\.gemini\antigravity\scratch\azure_web"
```

> [!NOTE]
> If you encounter PowerShell script execution policy errors with `npm.ps1`, either run commands using `npm.cmd` or set your session execution policy:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> ```

### 1. Backend Setup

1. Install backend Python dependencies:
   ```powershell
   python -m pip install -r backend/requirements.txt
   ```

2. Configure environment variables:
   Copy the `.env.example` file to create your local `.env`:
   ```powershell
   Copy-Item "backend\.env.example" "backend\.env"
   ```

3. Configure your student details in `backend\.env`:
   ```ini
   PORT=5000
   STUDENT_NAME=PRADEEP R
   ROLL_NUMBER=24EIR070
   AZURE_CONNECTION_STRING=
   DEMO_MODE=true
   CORS_ORIGINS=*
   ```

4. Start the Flask backend:
   ```powershell
   python backend/server.py
   ```
   The backend will start on **`http://127.0.0.1:5000`**.

### 2. Frontend Setup

In a new PowerShell window:

1. Install frontend packages:
   ```powershell
   npm.cmd install
   ```

2. Start the React development server:
   ```powershell
   npm.cmd start
   ```
   The dashboard will automatically open in your default browser at **`http://localhost:3000`**.

---

## ☁️ Azure IoT Hub Endpoint Setup

When your instructor provides the live Azure IoT Hub Event Hub-compatible connection string:

1. Open `backend/.env` (or configure your hosting provider's Environment Variables):
2. Paste the connection string into `AZURE_CONNECTION_STRING`:
   ```ini
   AZURE_CONNECTION_STRING=Endpoint=sb://<your-namespace>.servicebus.windows.net/;SharedAccessKeyName=<key-name>;SharedAccessKey=<your-key>;EntityPath=<your-entity-path>
   AZURE_CONSUMER_GROUP=$default
   DEMO_MODE=false
   ```
3. Restart the backend:
   ```powershell
   python backend/server.py
   ```
4. The dashboard will automatically transition from `🟡 Demo Mode` to `🟢 Live Azure IoT Hub` with connection status `CONNECTED`.

> [!CAUTION]
> **Security Notice**: Never commit `.env` or paste actual connection strings into Git repositories, source files, or pull requests. All `.env` files are ignored by `.gitignore`. If an Azure credential was ever exposed previously, request immediate credential rotation from the administrator.

---

## 🎮 Demo Mode (Simulated Testing)

If you do not have an active Azure connection string, Demo Mode runs automatically!

- Demo mode emits simulated ASCII telemetry every 3 seconds (e.g., `72,101,108,108,111` $\rightarrow$ `Hello`).
- It clearly tags the source as `DEMO MODE (SIMULATED)` with a distinct yellow badge so reviewers know it is running in local simulation.
- You can also click **⚡ Test Conversion (72,101,...)** directly on the dashboard to inject an instant test packet and verify conversion.

---

## 📡 REST API Reference

The backend provides a standardized REST API consumed by the React frontend:

| Endpoint | Method | Description | Sample Output |
| :--- | :---: | :--- | :--- |
| `GET /api/health` | `GET` | Service liveness probe | `{"status": "ok", "service": "azure-iot-telemetry-backend"}` |
| `GET /api/status` | `GET` | Azure connection state & student info | `{"azure_status": "CONNECTED", "demo_mode": false, "student_name": "PRADEEP R", "roll_number": "24EIR070"}` |
| `GET /api/telemetry/latest` | `GET` | Most recent telemetry event with all 6 fields | `{"student_name": "PRADEEP R", "roll_number": "24EIR070", "azure_status": "CONNECTED", "raw_ascii": "72,101,108,108,111", "converted_string": "Hello", "timestamp": "2026-10-25T15:30:00Z"}` |
| `GET /api/telemetry/history` | `GET` | Recent telemetry activity history (last 25 events) | `{"count": 16, "history": [...]}` |
| `POST /api/telemetry/simulate` | `POST` | Injects manual test payload | Payload: `{"payload": "72,101,108,108,111"}` |
| `GET /api/latest` | `GET` | Legacy backward compatibility endpoint | `{"message": "Hello", "timestamp": "2026-10-25T15:30:00Z"}` |

---

## 🧪 Automated Testing

Both backend and frontend contain automated unit test suites that verify conversion logic, range validation (0–127), API behavior, and React component rendering.

### 1. Run Backend Python Tests (Pytest)
```powershell
python -m pytest tests/ -v
```
**Expected Result**:
```text
tests/test_api.py::test_health_endpoint PASSED
tests/test_api.py::test_status_endpoint PASSED
tests/test_api.py::test_telemetry_latest_fields PASSED
tests/test_api.py::test_telemetry_simulate_endpoint PASSED
tests/test_api.py::test_telemetry_history_endpoint PASSED
tests/test_api.py::test_legacy_endpoint PASSED
tests/test_converter.py::test_convert_ascii_hello PASSED
tests/test_converter.py::test_convert_ascii_single_character PASSED
tests/test_converter.py::test_convert_ascii_invalid_out_of_range PASSED
tests/test_converter.py::test_convert_ascii_empty PASSED
tests/test_converter.py::test_parse_ascii_sequence_comma_separated PASSED
tests/test_converter.py::test_parse_ascii_sequence_with_whitespace PASSED
tests/test_converter.py::test_parse_ascii_sequence_json_array PASSED
tests/test_converter.py::test_parse_ascii_sequence_invalid PASSED
tests/test_converter.py::test_process_telemetry_payload_standard_string PASSED
tests/test_converter.py::test_process_telemetry_payload_bytes PASSED
tests/test_converter.py::test_process_telemetry_payload_json_data PASSED
tests/test_converter.py::test_process_telemetry_payload_json_ascii_str PASSED
tests/test_converter.py::test_process_telemetry_payload_invalid_ascii PASSED
tests/test_converter.py::test_process_telemetry_payload_empty PASSED

============================= 20 passed in 1.01s ==============================
```

### 2. Run Frontend React Tests (Jest)
```powershell
npm.cmd test -- --watchAll=false
```
**Expected Result**:
```text
PASS src/App.test.js
  √ renders Azure IoT Telemetry Dashboard header
  √ renders all 6 required assignment fields
  √ renders activity history table

Test Suites: 1 passed, 1 total
Tests:       3 passed, 3 total
Snapshots:   0 total
```

### 3. Verify Production Frontend Build
```powershell
npm.cmd run build
```
**Expected Result**:
```text
Compiled successfully.
File sizes after gzip:
  72.59 kB  build\static\js\main.97d38552.js
  2.53 kB   build\static\css\main.d6cbe52b.css
```

---

## 🌐 Deployment Instructions

### 1. Deploy Frontend to Vercel

1. Push your repository to GitHub:
   ```powershell
   git add .
   git commit -m "Complete Azure IoT telemetry dashboard implementation"
   git push origin main
   ```
2. Log in to [Vercel](https://vercel.com) using your GitHub account.
3. Click **Add New Project** and select `IIOT_project`.
4. Under **Framework Preset**, select **Create React App**.
5. Under **Environment Variables**, add:
   - `REACT_APP_API_BASE_URL`: URL of your hosted backend (e.g., `https://your-backend.onrender.com`).
   - `REACT_APP_STUDENT_NAME`: `PRADEEP R`
   - `REACT_APP_ROLL_NUMBER`: `24EIR070`
6. Click **Deploy**. Vercel will build the frontend and provide your live URL.

### 2. Deploy Backend (Recommended: Render / Railway)

Because Azure Event Hub requires an active background consumer process, deploy the backend to a free container or web service platform like [Render](https://render.com) or [Railway](https://railway.app):

1. Create a **Web Service** pointing to your `IIOT_project` repository.
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `gunicorn --bind 0.0.0.0:$PORT backend.server:app`
4. Set Environment Variables in Render/Railway dashboard:
   - `STUDENT_NAME`: `PRADEEP R`
   - `ROLL_NUMBER`: `24EIR070`
   - `AZURE_CONNECTION_STRING`: `<your instructor's connection string>`
   - `AZURE_CONSUMER_GROUP`: `$default`
   - `DEMO_MODE`: `false`
   - `CORS_ORIGINS`: `https://your-project.vercel.app`

---

## 🔧 Troubleshooting Guide

| Issue | Likely Cause | Solution |
| :--- | :--- | :--- |
| `npm.ps1 cannot be loaded` | PowerShell execution policy restricted | Run `npm.cmd` instead of `npm`, or execute `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`. |
| Backend connection lost on dashboard | Backend server is not running on port 5000 | Ensure `python backend/server.py` is started and listening on `http://127.0.0.1:5000`. |
| CORS error in browser console | Origin not permitted | Set `CORS_ORIGINS=*` in development, or set it to your exact Vercel frontend domain in production. |
| Invalid ASCII error on dashboard | Number > 127 or non-numeric value in payload | The converter strictly validates 0–127 byte range. Ensure the transmitter sends valid ASCII numbers. |
| `ENOSPC: no space left on device` | System drive C: full | Free 1–2 GB on drive C: by cleaning temporary files or old caches (`.cache`, Downloads, Temp). |

---

## 📌 Submission Checklist

- [x] **Student Name configured**: `PRADEEP R`
- [x] **Roll Number configured**: `24EIR070`
- [x] **Azure Connection Status displayed**: Live indicator with `CONNECTED`, `CONNECTING`, `DISCONNECTED`, `ERROR`, or `DEMO MODE`
- [x] **Received ASCII Values displayed**: Raw codes (e.g., `72,101,108,108,111`)
- [x] **Converted String displayed**: Decoded message (e.g., `Hello`)
- [x] **Last Event Timestamp displayed**: Formatted localized date & time
- [x] **ASCII Conversion tested**: `72,101,108,108,111` $\rightarrow$ `Hello` verified with 14 unit tests
- [x] **Backend unit tests passed**: 20/20 pytest tests passing
- [x] **Frontend unit tests passed**: 3/3 Jest tests passing
- [x] **Production build passed**: `npm run build` compiled cleanly
- [x] **Security verified**: Zero secrets, `.env` files, or access keys committed
- [x] **Vercel routing configured**: `vercel.json` SPA rewrites created
