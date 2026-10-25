import { render, screen, waitFor, act } from "@testing-library/react";
import AzureWeb from "./azure_web";

beforeEach(() => {
  jest.clearAllMocks();
  // Mock global fetch
  global.fetch = jest.fn((url) => {
    if (url.includes("/api/telemetry/latest")) {
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            student_name: "PRADEEP R",
            roll_number: "24EIR070",
            azure_status: "CONNECTED",
            raw_ascii: "72,101,108,108,111",
            converted_string: "Hello",
            timestamp: "2026-10-25T15:30:00Z",
            source: "azure",
            valid: true,
            error: null,
            demo_mode: false,
          }),
      });
    }

    if (url.includes("/api/telemetry/history")) {
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            history: [
              {
                id: 1,
                raw_ascii: "72,101,108,108,111",
                converted_string: "Hello",
                timestamp: "2026-10-25T15:30:00Z",
                source: "azure",
                valid: true,
              },
            ],
            count: 1,
          }),
      });
    }

    return Promise.reject(new Error("Unknown URL"));
  });
});

afterEach(() => {
  jest.restoreAllMocks();
});

test("renders Azure IoT Telemetry Dashboard header", async () => {
  await act(async () => {
    render(<AzureWeb />);
  });
  const heading = screen.getByRole("heading", {
    name: /Azure IoT Telemetry Dashboard/i,
  });
  expect(heading).toBeInTheDocument();
});

test("renders all 6 required assignment fields", async () => {
  await act(async () => {
    render(<AzureWeb />);
  });

  // 1. Student Name
  const studentNameElem = await screen.findByTestId("student-name");
  expect(studentNameElem).toBeInTheDocument();
  expect(studentNameElem).toHaveTextContent("PRADEEP R");

  // 2. Roll Number
  const rollNumberElem = await screen.findByTestId("roll-number");
  expect(rollNumberElem).toBeInTheDocument();
  expect(rollNumberElem).toHaveTextContent("24EIR070");

  // 3. Azure Connection Status
  const statusElem = await screen.findByTestId("azure-status");
  expect(statusElem).toBeInTheDocument();
  expect(statusElem).toHaveTextContent("CONNECTED");

  // 4. Received ASCII Values
  const asciiElem = await screen.findByTestId("received-ascii");
  expect(asciiElem).toBeInTheDocument();
  expect(asciiElem).toHaveTextContent("72,101,108,108,111");

  // 5. Converted String
  const convertedElem = await screen.findByTestId("converted-string");
  expect(convertedElem).toBeInTheDocument();
  expect(convertedElem).toHaveTextContent("Hello");

  // 6. Last Event Timestamp
  const timestampElem = await screen.findByTestId("event-timestamp");
  expect(timestampElem).toBeInTheDocument();
  expect(timestampElem.textContent).not.toBe("No events received yet");
});

test("renders activity history table", async () => {
  await act(async () => {
    render(<AzureWeb />);
  });

  const historyHeader = screen.getByText(/Live Telemetry Activity History/i);
  expect(historyHeader).toBeInTheDocument();

  await waitFor(() => {
    expect(screen.getByText("1 Events Logged")).toBeInTheDocument();
  });
});
