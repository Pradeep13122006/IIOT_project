"""
Telemetry and ASCII conversion utility.
Handles raw bytes, JSON strings, comma-separated ASCII codes, arrays, and error checking.
Valid ASCII range is 0 to 127.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


def convert_ascii_values(values: List[int]) -> Tuple[Optional[str], Optional[str]]:
    """
    Converts a list of integer values to an ASCII string.
    Validates that each code is an integer between 0 and 127.
    Returns: (converted_string, error_message)
    """
    if not values:
        return "", None

    invalid_items = []
    for val in values:
        if not isinstance(val, int) or val < 0 or val > 127:
            invalid_items.append(val)

    if invalid_items:
        return (
            None,
            f"Invalid ASCII value(s) detected: {invalid_items}. Valid ASCII range is 0-127.",
        )

    converted = "".join(chr(val) for val in values)
    return converted, None


def parse_ascii_sequence(text: str) -> Tuple[Optional[List[int]], Optional[str]]:
    """
    Parses a string representing ASCII values (e.g. "72,101,108,108,111" or "[72, 101, 108]")
    into a list of integers.
    Returns: (list_of_ints, error_message)
    """
    cleaned = text.strip()
    if not cleaned:
        return [], None

    # Check if it's formatted as a JSON list string e.g. "[72, 101, 108]"
    if cleaned.startswith("[") and cleaned.endswith("]"):
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, list):
                if all(isinstance(x, int) for x in parsed):
                    return parsed, None
                # Try converting elements if they are numeric strings
                return [int(x) for x in parsed], None
        except (json.JSONDecodeError, ValueError, TypeError):
            return None, f"Malformed JSON array: {cleaned}"

    # Handle comma-separated, space-separated, or semicolon-separated values
    # e.g. "72, 101, 108, 108, 111"
    delimiters = [",", " ", ";"]
    delimiter_used = ","
    for d in delimiters:
        if d in cleaned:
            delimiter_used = d
            break

    parts = [p.strip() for p in cleaned.split(delimiter_used) if p.strip()]
    if not parts:
        return [], None

    try:
        codes = [int(p) for p in parts]
        return codes, None
    except ValueError:
        return None, f"Non-numeric ASCII token encountered in: '{cleaned}'"


def process_telemetry_payload(
    raw_payload: Any,
    enqueued_time: Optional[datetime] = None,
    source: str = "azure",
) -> Dict[str, Any]:
    """
    Processes an incoming Azure IoT / Event Hubs message payload.
    Extracts raw ASCII values, converts to string, validates ranges,
    and returns a normalized dictionary.
    """
    timestamp = (
        enqueued_time.isoformat()
        if enqueued_time
        else datetime.now(timezone.utc).isoformat()
    )

    # 1. Normalize bytes to UTF-8 string
    if isinstance(raw_payload, bytes):
        try:
            text = raw_payload.decode("utf-8")
        except UnicodeDecodeError:
            text = raw_payload.decode("latin-1", errors="replace")
    elif isinstance(raw_payload, str):
        text = raw_payload
    else:
        text = str(raw_payload)

    text = text.strip()

    # Default payload structure
    result = {
        "raw_ascii": "",
        "converted_string": "",
        "timestamp": timestamp,
        "source": source,
        "valid": True,
        "error": None,
        "raw_payload": text,
    }

    if not text:
        result["error"] = "Empty telemetry payload received."
        result["valid"] = False
        return result

    # 2. Inspect if text is a JSON object with structured fields
    # e.g., {"ascii": "72,101,108,108,111"} or {"values": [72, 101]} or {"message": ...}
    ascii_input = None
    if text.startswith("{") and text.endswith("}"):
        try:
            parsed_json = json.loads(text)
            if isinstance(parsed_json, dict):
                # Search for known key names
                for key in ["ascii", "ascii_values", "values", "data", "payload", "message"]:
                    if key in parsed_json:
                        val = parsed_json[key]
                        if isinstance(val, list):
                            ascii_input = val
                            break
                        elif isinstance(val, str):
                            ascii_input = val
                            break
        except json.JSONDecodeError:
            pass

    if ascii_input is None:
        ascii_input = text

    # 3. Parse input into integer codes
    if isinstance(ascii_input, list):
        try:
            int_codes = [int(x) for x in ascii_input]
            parse_err = None
        except (ValueError, TypeError):
            int_codes, parse_err = None, f"Non-integer items in list: {ascii_input}"
    else:
        int_codes, parse_err = parse_ascii_sequence(str(ascii_input))

    if parse_err:
        result["raw_ascii"] = str(ascii_input)
        result["converted_string"] = str(ascii_input)  # Fallback display as-is
        result["error"] = parse_err
        result["valid"] = False
        return result

    # 4. Check if we have integer codes
    if int_codes is not None and len(int_codes) > 0:
        raw_ascii_str = ",".join(str(c) for c in int_codes)
        converted_str, conv_err = convert_ascii_values(int_codes)

        result["raw_ascii"] = raw_ascii_str
        if conv_err:
            result["converted_string"] = ""
            result["error"] = conv_err
            result["valid"] = False
        else:
            result["converted_string"] = converted_str
            result["valid"] = True
    else:
        # Plain text without ASCII integers
        result["raw_ascii"] = ""
        result["converted_string"] = text
        result["valid"] = True

    return result
