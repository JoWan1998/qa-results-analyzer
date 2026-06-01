import pandas as pd
from lxml import etree

def parse_selenium(file) -> pd.DataFrame:
    tree = etree.parse(file)
    root = tree.getroot()
    records = []

    for suite in root.iter("testsuite"):
        suite_name = suite.get("name", "")
        for case in suite.iter("testcase"):
            failed    = case.find("failure") is not None
            errored   = case.find("error") is not None
            skipped   = case.find("skipped") is not None
            success   = not failed and not errored and not skipped

            error_msg = ""
            if failed:
                error_msg = case.find("failure").get("message", "")
            elif errored:
                error_msg = case.find("error").get("message", "")

            records.append({
                "label":      f"{suite_name} > {case.get('name', '')}",
                "success":    success,
                "elapsed_ms": round(float(case.get("time", 0)) * 1000),
                "status":     "passed" if success else ("skipped" if skipped else "failed"),
                "file":       case.get("classname", ""),
                "error":      error_msg,
            })

    return pd.DataFrame(records)