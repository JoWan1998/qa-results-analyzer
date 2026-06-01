import pandas as pd

def compute_metrics(df: pd.DataFrame) -> dict:
    total     = len(df)
    passed    = df["success"].sum()
    failed    = total - passed
    pass_rate = round(passed / total * 100, 1) if total else 0

    avg_ms  = round(df["elapsed_ms"].mean(), 1)
    p90_ms  = round(df["elapsed_ms"].quantile(0.90), 1)
    p95_ms  = round(df["elapsed_ms"].quantile(0.95), 1)

    by_label = (
        df.groupby("label")
        .agg(total=("success","count"), passed=("success","sum"), avg_ms=("elapsed_ms","mean"))
        .assign(pass_rate=lambda x: (x.passed/x.total*100).round(1))
        .sort_values("pass_rate")
        .reset_index()
    )

    failed_df = df[~df["success"]]

    return {
        "total": total, "passed": int(passed),
        "failed": int(failed), "pass_rate": pass_rate,
        "avg_ms": avg_ms, "p90_ms": p90_ms, "p95_ms": p95_ms,
        "by_label": by_label, "failed_df": failed_df,
    }