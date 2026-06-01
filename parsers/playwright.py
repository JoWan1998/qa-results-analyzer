import pandas as pd, json

def parse_playwright(file) -> pd.DataFrame:
    data = json.load(file)
    records = []
    for suite in data.get("suites", []):
        for spec in suite.get("specs", []):
            for test in spec.get("tests", []):
                for result in test.get("results", []):
                    records.append({
                        "label":      spec.get("title", ""),
                        "success":    result.get("status") == "passed",
                        "elapsed_ms": result.get("duration", 0),
                        "status":     result.get("status", ""),
                        "file":       suite.get("file", ""),
                        "error":      result.get("error", {}).get("message", "") if result.get("error") else "",
                    })
    return pd.DataFrame(records)