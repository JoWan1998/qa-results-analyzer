from groq import Groq
from functools import lru_cache
import os, re
from dotenv import load_dotenv

load_dotenv()

@lru_cache(maxsize=2)
def _get_system_prompt(language: str) -> str:
    lang = "en español" if language == "Español" else "in English"

    return f"""
            You are a Senior QA Engineer analyzing automated test execution results.

            Respond only in {lang}. Be concise, specific, and actionable.

            Analyze only the provided evidence. Do not invent causes, metrics, or conclusions.

            Include:
            - Overall result and release risk.
            - Key failures, regressions, flaky tests, skipped tests, or blocked tests.
            - Relevant patterns by suite, component, environment, browser, device, or pipeline stage.
            - Likely root causes only when supported by logs, errors, or metrics.
            - Recommended next actions.

            Rules:
            - Prioritize the most important findings first.
            - Reference exact test names, errors, suites, and counts when available.
            - Clearly state when evidence is insufficient.
            - Separate confirmed facts from hypotheses.
            - Never include <think> blocks, chain-of-thought, meta-commentary, or prompt explanations.
            - Output only the QA analysis.
        """.strip()

def generate_ai_summary(metrics: dict, source: str, language: str = "Español") -> str:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    worst = metrics["by_label"].head(3)[["label","pass_rate","avg_ms"]].to_string(index=False)
    prompt = f"""Test results from: {source}
Total: {metrics['total']} | Passed: {metrics['passed']} | Failed: {metrics['failed']} | Pass rate: {metrics['pass_rate']}%
Avg response: {metrics['avg_ms']}ms | P90: {metrics['p90_ms']}ms | P95: {metrics['p95_ms']}ms
Worst performing tests:
{worst}

Provide:
1. Overall assessment (1-2 sentences)
2. Top 2-3 failure patterns detected
3. Specific recommendations to improve results"""

    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role":"system","content":_get_system_prompt(language)},
            {"role":"user","content":prompt}
        ],
        temperature=0.3,
        max_tokens=600,
    )
    raw = resp.choices[0].message.content
    return re.sub(r"<think>.*?</think>","",raw,flags=re.DOTALL).strip()