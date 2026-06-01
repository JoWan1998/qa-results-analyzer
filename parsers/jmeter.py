import pandas as pd
from lxml import etree

def parse_jmeter(file) -> pd.DataFrame:
    tree = etree.parse(file)
    root = tree.getroot()
    records = []
    for sample in root.iter("httpSample", "sample"):
        records.append({
            "label":      sample.get("lb", ""),
            "success":    sample.get("s", "false") == "true",
            "elapsed_ms": int(sample.get("t", 0)),
            "bytes":      int(sample.get("by", 0)),
            "response":   sample.get("rc", ""),
            "timestamp":  int(sample.get("ts", 0)),
            "thread":     sample.get("tn", ""),
        })
    return pd.DataFrame(records)