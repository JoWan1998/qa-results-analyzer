import pandas as pd
from lxml import etree
import io


CSV_COLUMNS = {
    "timeStamp":      "timestamp",
    "elapsed":        "elapsed_ms",
    "label":          "label",
    "responseCode":   "response",
    "responseMessage":"response_message",
    "threadName":     "thread",
    "success":        "success",
    "failureMessage": "error",
    "bytes":          "bytes",
    "sentBytes":      "sent_bytes",
    "Latency":        "latency_ms",
    "Connect":        "connect_ms",
    "URL":            "url",
}


def _parse_csv(file) -> pd.DataFrame:
    df = pd.read_csv(file, low_memory=False)

    # Normalize column names — keep only known columns that exist
    rename = {k: v for k, v in CSV_COLUMNS.items() if k in df.columns}
    df = df.rename(columns=rename)

    # success: JMeter writes "true"/"false" as strings
    if "success" in df.columns:
        df["success"] = df["success"].astype(str).str.lower() == "true"

    # elapsed is already in ms in CSV format
    if "elapsed_ms" not in df.columns:
        raise ValueError("Column 'elapsed' not found — is this a valid JMeter CSV?")

    df["elapsed_ms"] = pd.to_numeric(df["elapsed_ms"], errors="coerce").fillna(0).astype(int)

    # Derive status from success
    df["status"] = df["success"].map({True: "passed", False: "failed"})

    # error: fill missing
    if "error" not in df.columns:
        df["error"] = ""
    df["error"] = df["error"].fillna("").astype(str)

    # file/suite: use URL path if available, else empty
    if "url" in df.columns:
        df["file"] = df["url"].fillna("").astype(str)
    else:
        df["file"] = ""

    # response: coerce to string
    if "response" not in df.columns:
        df["response"] = ""
    df["response"] = df["response"].fillna("").astype(str)

    return df[[
        "label", "success", "elapsed_ms", "status",
        "file", "error", "response",
        *[c for c in ["bytes", "latency_ms", "thread", "timestamp"] if c in df.columns]
    ]]


def _parse_xml(file) -> pd.DataFrame:
    content = file.read() if hasattr(file, "read") else open(file, "rb").read()
    tree = etree.fromstring(content)
    records = []

    for sample in tree.iter("httpSample", "sample"):
        success = sample.get("s", "false").lower() == "true"
        records.append({
            "label":      sample.get("lb", ""),
            "success":    success,
            "elapsed_ms": int(sample.get("t", 0)),
            "bytes":      int(sample.get("by", 0)),
            "response":   sample.get("rc", ""),
            "timestamp":  int(sample.get("ts", 0)),
            "thread":     sample.get("tn", ""),
            "error":      "" if success else sample.get("rm", ""),
            "status":     "passed" if success else "failed",
            "file":       sample.get("lb", ""),
        })

    return pd.DataFrame(records)


def parse_jmeter(file) -> pd.DataFrame:
    """
    Parse a JMeter results file (.jtl).
    Auto-detects CSV vs XML format by reading the first line.
    """
    # Read first line to detect format
    if hasattr(file, "read"):
        first_bytes = file.read(512)
        file.seek(0)
    else:
        with open(file, "rb") as f:
            first_bytes = f.read(512)

    first_line = first_bytes.decode("utf-8", errors="ignore").strip().splitlines()[0]

    # XML starts with <?xml or <testResults
    is_xml = first_line.startswith("<?xml") or first_line.startswith("<testResults") or first_line.startswith("<")

    if is_xml:
        return _parse_xml(file)
    else:
        return _parse_csv(file)