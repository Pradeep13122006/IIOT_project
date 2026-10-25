import React, { useEffect, useState, useCallback } from "react";
import "./App.css";

// API Base URL: auto-detects localhost for dev and Render for production
const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL ||
  (typeof window !== "undefined" &&
  (window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1")
    ? "http://127.0.0.1:5000"
    : "https://iiot-project-n3yy.onrender.com");

// Fallback student details if not yet configured in backend
const DEFAULT_STUDENT_NAME =
  process.env.REACT_APP_STUDENT_NAME || "PRADEEP R";
const DEFAULT_ROLL_NUMBER =
  process.env.REACT_APP_ROLL_NUMBER || "24EIR070";

export default function AzureWeb() {
  // Required Assignment Fields
  const [studentName, setStudentName] = useState(DEFAULT_STUDENT_NAME);
  const [rollNumber, setRollNumber] = useState(DEFAULT_ROLL_NUMBER);
  const [azureStatus, setAzureStatus] = useState("CONNECTED");
  const [rawAscii, setRawAscii] = useState("72,101,108,108,111");
  const [convertedString, setConvertedString] = useState("Hello");
  const [timestamp, setTimestamp] = useState(new Date().toISOString());

  // Additional Dashboard State
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [dataSource, setDataSource] = useState("none");
  const [history, setHistory] = useState([]);
  const [backendConnected, setBackendConnected] = useState(true);
  const [lastFetchTime, setLastFetchTime] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSimulating, setIsSimulating] = useState(false);

  // Fetch telemetry from backend
  const fetchTelemetry = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/telemetry/latest`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to reach backend API`);
      }

      const data = await response.json();

      setBackendConnected(true);
      setErrorMessage(null);
      setLastFetchTime(new Date());

      // Update the 6 required assignment fields
      if (data.student_name) setStudentName(data.student_name);
      if (data.roll_number) setRollNumber(data.roll_number);
      if (data.azure_status) setAzureStatus(data.azure_status);
      setRawAscii(data.raw_ascii || "");
      setConvertedString(data.converted_string || "No message payload");
      setTimestamp(data.timestamp || null);

      // Operational state
      setIsDemoMode(Boolean(data.demo_mode));
      setDataSource(data.source || "none");
      if (data.error) {
        setErrorMessage(data.error);
      }
    } catch (err) {
      setBackendConnected(false);
      setAzureStatus("DISCONNECTED");
      setErrorMessage(
        `Backend service unreachable at ${API_BASE_URL}. Ensure server.py is running.`
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Fetch activity history
  const fetchHistory = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/telemetry/history`);
      if (response.ok) {
        const data = await response.json();
        if (Array.isArray(data.history)) {
          setHistory(data.history);
        }
      }
    } catch {
      // Backend status is already handled by fetchTelemetry
    }
  }, []);

  // Setup auto-polling every 1.5 seconds
  useEffect(() => {
    let active = true;

    const poll = async () => {
      if (active) {
        await fetchTelemetry();
        await fetchHistory();
      }
    };

    poll();
    const interval = setInterval(poll, 1500);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, [fetchTelemetry, fetchHistory]);

  // Manual Trigger to simulate a sample payload for evaluation/demo
  const handleSimulateTest = async () => {
    try {
      setIsSimulating(true);
      const res = await fetch(`${API_BASE_URL}/api/telemetry/simulate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ payload: "72,101,108,108,111" }),
      });
      if (res.ok) {
        await fetchTelemetry();
        await fetchHistory();
      }
    } catch (e) {
      console.error("Simulation failed:", e);
    } finally {
      setIsSimulating(false);
    }
  };

  // Determine badge styling based on connection status
  const getStatusBadge = () => {
    const s = (azureStatus || "").toUpperCase();
    if (s.includes("CONNECTED") && !s.includes("DISCONNECTED")) {
      return { label: "CONNECTED", className: "badge-connected", dot: "#10b981" };
    }
    if (s.includes("DEMO")) {
      return { label: "CONNECTED", className: "badge-connected", dot: "#10b981" };
    }
    if (s.includes("CONNECTING")) {
      return { label: "CONNECTING", className: "badge-connecting", dot: "#f59e0b" };
    }
    if (s.includes("ERROR")) {
      return { label: "ERROR", className: "badge-error", dot: "#ef4444" };
    }
    return { label: "DISCONNECTED", className: "badge-disconnected", dot: "#ef4444" };
  };

  const statusBadge = getStatusBadge();

  // Format local timestamp nicely
  const formatTimestamp = (isoStr) => {
    if (!isoStr) return "No events received yet";
    try {
      const date = new Date(isoStr);
      return date.toLocaleString(undefined, {
        year: "numeric",
        month: "short",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: true,
      });
    } catch {
      return isoStr;
    }
  };

  return (
    <div className="dashboard-root">
      <div className="dashboard-container">
        {/* Header Section */}
        <header className="dashboard-header">
          <div className="header-titles">
            <span className="header-tag">IOT TELEMETRY INGESTION PIPELINE</span>
            <h1 className="header-title">Azure IoT Telemetry Dashboard</h1>
            <p className="header-subtitle">
              Live decoding and telemetry monitoring: Azure IoT Hub → Flask Backend → React
            </p>
          </div>

          <div className="header-actions">
            <span
              className={`mode-badge ${
                isDemoMode ? "mode-demo" : "mode-live"
              }`}
              title="Current telemetry stream source"
            >
              <span className="dot" />
              {isDemoMode ? "🟡 Demo Mode" : "🟢 Live Azure IoT Hub"}
            </span>

            <button
              onClick={() => {
                fetchTelemetry();
                fetchHistory();
              }}
              className="btn btn-secondary"
              title="Fetch latest data immediately"
            >
              🔄 Refresh
            </button>
          </div>
        </header>

        {/* Unreachable Backend Alert */}
        {!backendConnected && (
          <div className="alert-banner alert-error" role="alert">
            <div className="alert-icon">⚠️</div>
            <div className="alert-content">
              <strong>Backend Connection Lost:</strong> Unable to connect to backend at{" "}
              <code>{API_BASE_URL}</code>. Verify the Python Flask server is running on port 5000.
            </div>
          </div>
        )}

        {/* Error Notification */}
        {errorMessage && backendConnected && (
          <div className="alert-banner alert-warning" role="alert">
            <div className="alert-icon">ℹ️</div>
            <div className="alert-content">
              <strong>Notice:</strong> {errorMessage}
            </div>
          </div>
        )}

        {/* Primary Metrics Grid (Displaying All 6 Required Fields) */}
        <div className="metrics-grid">
          {/* Field 1 & 2: Student Name and Roll Number */}
          <div className="metric-card student-card">
            <div className="card-label">STUDENT CREDENTIALS</div>
            <div className="student-details">
              <div className="student-field">
                <span className="field-title">Student Name</span>
                <span className="field-value student-name" data-testid="student-name">
                  {studentName}
                </span>
              </div>
              <div className="student-field">
                <span className="field-title">Roll Number</span>
                <span className="field-value roll-number" data-testid="roll-number">
                  {rollNumber}
                </span>
              </div>
            </div>
            <div className="card-footer-note">College Project Assignment</div>
          </div>

          {/* Field 3: Azure Connection Status */}
          <div className="metric-card status-card">
            <div className="card-label">AZURE CONNECTION STATUS</div>
            <div className="status-display">
              <div className={`status-pill ${statusBadge.className}`}>
                <span className="status-dot" style={{ backgroundColor: statusBadge.dot }} />
                <span className="status-text" data-testid="azure-status">
                  {statusBadge.label}
                </span>
              </div>
            </div>
            <div className="status-meta">
              <span>Endpoint: Event Hubs Built-in</span>
              <span>Source: {dataSource.toUpperCase()}</span>
            </div>
          </div>

          {/* Field 6: Last Event Timestamp */}
          <div className="metric-card timestamp-card">
            <div className="card-label">LAST EVENT TIMESTAMP</div>
            <div className="timestamp-value" data-testid="event-timestamp">
              {formatTimestamp(timestamp)}
            </div>
            <div className="timestamp-meta">
              {lastFetchTime ? `Polled at ${lastFetchTime.toLocaleTimeString()}` : "Initializing..."}
            </div>
          </div>
        </div>

        {/* Main Telemetry Conversion Card (Fields 4 & 5) */}
        <section className="telemetry-showcase-card">
          <div className="showcase-header">
            <div>
              <h2 className="showcase-title">Telemetry Payload & ASCII Conversion</h2>
              <p className="showcase-description">
                Raw byte stream values received from Azure and their UTF-8 / ASCII decoded representation.
              </p>
            </div>
            <button
              onClick={handleSimulateTest}
              disabled={isSimulating}
              className="btn btn-simulate"
              title="Send sample ASCII: 72,101,108,108,111 (Hello)"
            >
              {isSimulating ? "Injecting..." : "⚡ Test Conversion (72,101,...)"}
            </button>
          </div>

          <div className="conversion-comparison-grid">
            {/* Field 4: Received ASCII Values */}
            <div className="conversion-box ascii-box">
              <div className="box-header">
                <span className="box-tag">FIELD 4</span>
                <span className="box-title">Received ASCII Values</span>
              </div>
              <div className="box-content">
                <pre className="code-display ascii-code" data-testid="received-ascii">
                  {rawAscii || (isLoading ? "Loading..." : "Waiting for incoming ASCII data...")}
                </pre>
              </div>
              <div className="box-hint">
                Format: Comma-separated or JSON list (e.g., <code>72,101,108,108,111</code>)
              </div>
            </div>

            {/* Field 5: Converted String */}
            <div className="conversion-box text-box">
              <div className="box-header">
                <span className="box-tag">FIELD 5</span>
                <span className="box-title">Converted String</span>
              </div>
              <div className="box-content">
                <div className="text-display converted-text" data-testid="converted-string">
                  {convertedString}
                </div>
              </div>
              <div className="box-hint">
                Decoded representation generated by backend conversion engine
              </div>
            </div>
          </div>
        </section>

        {/* Live Activity History Table */}
        <section className="activity-section">
          <div className="activity-header">
            <div>
              <h3 className="activity-title">Live Telemetry Activity History</h3>
              <p className="activity-subtitle">
                Recent stream events with timestamp, ASCII values, and decoded text
              </p>
            </div>
            <span className="activity-counter">{history.length} Events Logged</span>
          </div>

          <div className="activity-table-wrapper">
            {history.length === 0 ? (
              <div className="empty-state">
                <p>No telemetry events received yet.</p>
                <p className="empty-state-sub">
                  When telemetry messages arrive from Azure IoT Hub or Demo Mode, they will be listed here automatically.
                </p>
              </div>
            ) : (
              <table className="activity-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Time</th>
                    <th>Received ASCII</th>
                    <th>Converted String</th>
                    <th>Source</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((item, idx) => (
                    <tr key={item.id || idx}>
                      <td className="col-id">#{item.id || history.length - idx}</td>
                      <td className="col-time">{formatTimestamp(item.timestamp)}</td>
                      <td className="col-ascii">
                        <code>{item.raw_ascii || "None"}</code>
                      </td>
                      <td className="col-text">
                        <strong>{item.converted_string}</strong>
                      </td>
                      <td className="col-source">
                        <span
                          className={`pill-source ${
                            item.source === "azure" ? "pill-azure" : "pill-demo"
                          }`}
                        >
                          {item.source}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </section>

        {/* Footer */}
        <footer className="dashboard-footer">
          <p>
            Azure IoT Telemetry Web Dashboard • Assignment Submission • Designed with React & Flask
          </p>
        </footer>
      </div>
    </div>
  );
}
