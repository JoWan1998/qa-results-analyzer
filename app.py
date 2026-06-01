import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from parsers.jmeter import parse_jmeter
from parsers.playwright import parse_playwright
from parsers.selenium import parse_selenium
from parsers.sample_data import (
    generate_sample_jmeter,
    generate_sample_playwright,
    generate_sample_selenium,
)
from analyzer import compute_metrics
from ai_summary import generate_ai_summary


st.set_page_config(
    page_title="QA Results Analyzer",
    page_icon="📊",
    layout="wide",
)

st.title("QA Results Analyzer")
st.caption("Analyze JMeter · Playwright · Selenium results — Powered by Groq AI")

# sidebar

with st.sidebar:
    st.header("Configuration")

    source = st.selectbox(
        "Source",
        ["JMeter XML", "Playwright JSON", "Selenium / JUnit XML"],
        help="JMeter: .jtl XML | Playwright: --reporter=json | Selenium: --junitxml",
    )

    language = st.selectbox("AI language", ["Español", "English"])

    use_sample = st.toggle("Use sample data (demo)", value=True)

    st.divider()
    st.caption("Built by José Orlando Wannan Escobar")
    st.caption("[GitHub](https://github.com/JoWan1998) · [LinkedIn](https://linkedin.com/in/josewannan1998)")

# Source config — file type and labels per source 

SOURCE_CONFIG = {
    "JMeter XML": {
        "ext":        ["jtl", "xml"],
        "ext_label":  ".jtl / .xml",
        "parser":     parse_jmeter,
        "sample_fn":  generate_sample_jmeter,
        "help":       "Generate with JMeter: Run > Save Results (.jtl)",
    },
    "Playwright JSON": {
        "ext":        ["json"],
        "ext_label":  ".json",
        "parser":     parse_playwright,
        "sample_fn":  generate_sample_playwright,
        "help":       "Generate with: playwright test --reporter=json > results.json",
    },
    "Selenium / JUnit XML": {
        "ext":        ["xml"],
        "ext_label":  ".xml",
        "parser":     parse_selenium,
        "sample_fn":  generate_sample_selenium,
        "help":       "Generate with: pytest --junitxml=results.xml",
    },
}

cfg = SOURCE_CONFIG[source]

# Load data 

df = None

if use_sample:
    df = cfg["sample_fn"]()
else:
    st.info(
        f"**{source}** — expected format: `{cfg['ext_label']}` \n\n {cfg['help']}",
        icon="📂",
    )
    uploaded = st.file_uploader(
        f"Upload your {source} results file",
        type=cfg["ext"],
        help=cfg["help"],
    )
    if uploaded:
        with st.spinner(f"Parsing {uploaded.name}..."):
            try:
                df = cfg["parser"](uploaded)
                st.success(f"Loaded **{len(df)}** test records from `{uploaded.name}`")
            except Exception as e:
                st.error(f"Could not parse file: {e}")
                st.stop()

if df is None or df.empty:
    if use_sample:
        st.warning("Sample data is empty — this should not happen. Check sample_data.py.")
    else:
        st.info("Upload a file above to get started, or enable **Use sample data** in the sidebar.")
    st.stop()

#  Compute metrics 

m = compute_metrics(df)

#  KPI row 

st.subheader("Summary")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total",      m["total"])
c2.metric("Passed",     m["passed"],  delta=None)
c3.metric("Failed",     m["failed"],  delta=f"-{m['failed']}" if m["failed"] else None,  delta_color="inverse")
c4.metric("Pass rate",  f"{m['pass_rate']}%")
c5.metric("Avg resp.",  f"{m['avg_ms']} ms")

st.divider()

#  Tabs 

tab_summary, tab_charts, tab_ai = st.tabs(["📋 XML Summary", "📈 Charts", "🤖 AI Analysis"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — XML Summary
# ══════════════════════════════════════════════════════════════════════════════

with tab_summary:

    st.subheader("Test results data")

    #  Filters 
    col_f1, col_f2, col_f3 = st.columns([2, 1, 1])

    with col_f1:
        search = st.text_input("Search by name", placeholder="e.g. login, checkout...")

    with col_f2:
        status_filter = st.selectbox(
            "Status",
            ["All", "Passed", "Failed", "Skipped"],
        )

    with col_f3:
        if "file" in df.columns and df["file"].nunique() > 1:
            file_options = ["All"] + sorted(df["file"].dropna().unique().tolist())
            file_filter = st.selectbox("File / Suite", file_options)
        else:
            file_filter = "All"

    #  Apply filters 
    filtered = df.copy()

    if search:
        filtered = filtered[filtered["label"].str.contains(search, case=False, na=False)]

    if status_filter != "All":
        filtered = filtered[filtered["status"].str.lower() == status_filter.lower()] \
            if "status" in filtered.columns \
            else filtered[filtered["success"] == (status_filter == "Passed")]

    if file_filter != "All" and "file" in filtered.columns:
        filtered = filtered[filtered["file"] == file_filter]

    #  Stats row 
    st.caption(f"Showing **{len(filtered)}** of **{len(df)}** records")

    # Table 
    display_cols = ["label", "status", "elapsed_ms", "file"]
    if "response" in filtered.columns:
        display_cols.append("response")
    if "error" in filtered.columns:
        display_cols.append("error")
    display_cols = [c for c in display_cols if c in filtered.columns]

    # Color status column
    def color_status(val):
        if str(val).lower() == "passed":
            return "background-color: #d4edda; color: #155724"
        elif str(val).lower() == "failed":
            return "background-color: #f8d7da; color: #721c24"
        elif str(val).lower() == "skipped":
            return "background-color: #fff3cd; color: #856404"
        return ""

    display_df = filtered[display_cols].rename(columns={
        "label":      "Test name",
        "status":     "Status",
        "elapsed_ms": "Duration (ms)",
        "file":       "File / Suite",
        "response":   "HTTP code",
        "error":      "Error message",
    })
    styled = display_df.style.map(
        color_status,
        subset=["Status"] if "Status" in display_df.columns else []
    )

    st.dataframe(styled, width="stretch", height=420)

    #  Failed tests detail
    failed_df = df[~df["success"]]
    if not failed_df.empty:
        with st.expander(f"Failed tests detail ({len(failed_df)} cases)"):
            for _, row in failed_df.iterrows():
                with st.container():
                    st.markdown(f"**{row['label']}**")
                    if row.get("error"):
                        st.code(row["error"], language="text")
                    cols = st.columns(3)
                    cols[0].caption(f"Duration: {row['elapsed_ms']} ms")
                    if "file" in row:
                        cols[1].caption(f"File: {row['file']}")
                    if "response" in row:
                        cols[2].caption(f"HTTP: {row['response']}")
                    st.divider()

    #  Download 
    csv = filtered[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered results as CSV",
        data=csv,
        file_name="qa_results_filtered.csv",
        mime="text/csv",
    )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Charts
# ══════════════════════════════════════════════════════════════════════════════

with tab_charts:

    #  Row 1: Pass rate by test + Response time distribution ─
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Pass rate by test")
        by_label = m["by_label"].sort_values("pass_rate")
        fig_bar = px.bar(
            by_label,
            x="pass_rate",
            y="label",
            orientation="h",
            color="pass_rate",
            color_continuous_scale="RdYlGn",
            range_color=[0, 100],
            labels={"pass_rate": "Pass rate (%)", "label": ""},
            text="pass_rate",
        )
        fig_bar.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_bar.update_layout(
            coloraxis_showscale=False,
            margin=dict(l=0, r=40, t=20, b=0),
            height=380,
        )
        st.plotly_chart(fig_bar, width='stretch')

    with col2:
        st.subheader("Response time distribution")
        fig_hist = px.histogram(
            df,
            x="elapsed_ms",
            nbins=30,
            color_discrete_sequence=["#1D9E75"],
            labels={"elapsed_ms": "Duration (ms)", "count": "Tests"},
        )
        fig_hist.add_vline(x=m["avg_ms"],  line_dash="dash", line_color="#185FA5", annotation_text=f"Avg {m['avg_ms']}ms")
        fig_hist.add_vline(x=m["p90_ms"],  line_dash="dot",  line_color="#854F0B", annotation_text=f"P90 {m['p90_ms']}ms")
        fig_hist.add_vline(x=m["p95_ms"],  line_dash="dot",  line_color="#A32D2D", annotation_text=f"P95 {m['p95_ms']}ms")
        fig_hist.update_layout(margin=dict(l=0, r=0, t=20, b=0), height=380)
        st.plotly_chart(fig_hist, width='stretch')

    #  Row 2: Pass/Fail donut + Top slowest tests 
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Overall result")
        fig_pie = go.Figure(go.Pie(
            labels=["Passed", "Failed", "Skipped"],
            values=[
                m["passed"],
                m["failed"],
                int(df["status"].eq("skipped").sum()) if "status" in df.columns else 0,
            ],
            hole=0.55,
            marker_colors=["#1D9E75", "#E24B4A", "#EF9F27"],
        ))
        fig_pie.update_traces(textinfo="percent+label")
        fig_pie.update_layout(
            showlegend=False,
            margin=dict(l=0, r=0, t=20, b=0),
            height=320,
        )
        st.plotly_chart(fig_pie, width='stretch')

    with col4:
        st.subheader("Top 10 slowest tests")
        slowest = df.nlargest(10, "elapsed_ms")[["label", "elapsed_ms", "success"]].copy()
        slowest["color"] = slowest["success"].map({True: "#1D9E75", False: "#E24B4A"})
        fig_slow = px.bar(
            slowest,
            x="elapsed_ms",
            y="label",
            orientation="h",
            color="success",
            color_discrete_map={True: "#1D9E75", False: "#E24B4A"},
            labels={"elapsed_ms": "Duration (ms)", "label": "", "success": "Passed"},
        )
        fig_slow.update_layout(
            margin=dict(l=0, r=0, t=20, b=0),
            height=320,
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig_slow, width='stretch')

    #  Row 3: Response time per test (box plot) 
    st.subheader("Response time spread per test")
    fig_box = px.box(
        df,
        x="elapsed_ms",
        y="label",
        color_discrete_sequence=["#185FA5"],
        labels={"elapsed_ms": "Duration (ms)", "label": ""},
    )
    fig_box.update_layout(margin=dict(l=0, r=0, t=20, b=0), height=420)
    st.plotly_chart(fig_box, width='stretch')

    #  JMeter-only: response codes chart 
    if "response" in df.columns:
        st.subheader("HTTP response codes")
        resp_counts = df["response"].value_counts().reset_index()
        resp_counts.columns = ["code", "count"]
        resp_counts["color"] = resp_counts["code"].apply(
            lambda x: "#1D9E75" if str(x).startswith("2")
            else "#E24B4A" if str(x).startswith("5")
            else "#EF9F27"
        )
        fig_resp = px.bar(
            resp_counts,
            x="code",
            y="count",
            color="code",
            color_discrete_sequence=["#1D9E75", "#EF9F27", "#E24B4A", "#185FA5"],
            labels={"code": "HTTP code", "count": "Requests"},
        )
        fig_resp.update_layout(showlegend=False, margin=dict(l=0, r=0, t=20, b=0), height=300)
        st.plotly_chart(fig_resp, width='stretch')

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — AI Analysis
# ══════════════════════════════════════════════════════════════════════════════

with tab_ai:
    st.caption("Groq analyzes your metrics and detects failure patterns automatically.")

    if st.button("Generate AI summary", type="primary"):
        with st.spinner("Analyzing results with AI..."):
            summary = generate_ai_summary(m, source, language)

        st.markdown(summary)
        st.divider()

        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                "Download summary (.txt)",
                data=summary,
                file_name="qa_ai_summary.txt",
                mime="text/plain",
            )
        with col_dl2:
            st.download_button(
                "Download filtered CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="qa_full_results.csv",
                mime="text/csv",
            )