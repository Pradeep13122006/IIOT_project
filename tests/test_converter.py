"""
Tests for ASCII decoding and payload processing.
"""

import pytest
from backend.converter import (
    convert_ascii_values,
    parse_ascii_sequence,
    process_telemetry_payload,
)


def test_convert_ascii_hello():
    codes = [72, 101, 108, 108, 111]
    text, err = convert_ascii_values(codes)
    assert err is None
    assert text == "Hello"


def test_convert_ascii_single_character():
    codes = [65]
    text, err = convert_ascii_values(codes)
    assert err is None
    assert text == "A"


def test_convert_ascii_invalid_out_of_range():
    # ASCII is only 0 to 127
    codes = [72, 250, 101]
    text, err = convert_ascii_values(codes)
    assert text is None
    assert "Invalid ASCII value(s) detected: [250]" in err


def test_convert_ascii_empty():
    text, err = convert_ascii_values([])
    assert err is None
    assert text == ""


def test_parse_ascii_sequence_comma_separated():
    codes, err = parse_ascii_sequence("72,101,108,108,111")
    assert err is None
    assert codes == [72, 101, 108, 108, 111]


def test_parse_ascii_sequence_with_whitespace():
    codes, err = parse_ascii_sequence("  72 ,  101,  108, 108 , 111  ")
    assert err is None
    assert codes == [72, 101, 108, 108, 111]


def test_parse_ascii_sequence_json_array():
    codes, err = parse_ascii_sequence("[72, 101, 108, 108, 111]")
    assert err is None
    assert codes == [72, 101, 108, 108, 111]


def test_parse_ascii_sequence_invalid():
    codes, err = parse_ascii_sequence("72,xyz,108")
    assert codes is None
    assert "Non-numeric ASCII token encountered" in err


def test_process_telemetry_payload_standard_string():
    res = process_telemetry_payload("72,101,108,108,111")
    assert res["valid"] is True
    assert res["raw_ascii"] == "72,101,108,108,111"
    assert res["converted_string"] == "Hello"
    assert res["error"] is None


def test_process_telemetry_payload_bytes():
    res = process_telemetry_payload(b"72,101,108,108,111")
    assert res["valid"] is True
    assert res["raw_ascii"] == "72,101,108,108,111"
    assert res["converted_string"] == "Hello"


def test_process_telemetry_payload_json_data():
    json_data = '{"data": [72, 101, 108, 108, 111]}'
    res = process_telemetry_payload(json_data)
    assert res["valid"] is True
    assert res["raw_ascii"] == "72,101,108,108,111"
    assert res["converted_string"] == "Hello"


def test_process_telemetry_payload_json_ascii_str():
    json_data = '{"ascii": "72,101,108,108,111"}'
    res = process_telemetry_payload(json_data)
    assert res["valid"] is True
    assert res["raw_ascii"] == "72,101,108,108,111"
    assert res["converted_string"] == "Hello"


def test_process_telemetry_payload_invalid_ascii():
    res = process_telemetry_payload("72,200,101")
    assert res["valid"] is False
    assert res["raw_ascii"] == "72,200,101"
    assert "Invalid ASCII value" in res["error"]


def test_process_telemetry_payload_empty():
    res = process_telemetry_payload("")
    assert res["valid"] is False
    assert "Empty telemetry payload" in res["error"]
