# 📊 QA Results Analyzer

> Upload your test results and get instant metrics, charts, and AI-powered insights.
> Supports JMeter, Playwright, and Selenium. Built with Python & Streamlit. Free and open source.

---

## 🚀 Live Demo

- [ai-test-case-generator-jose-wannan.streamlit.app](https://app-results-analyzer-jose-wannan.streamlit.app/)

> No login required. Use the sample data toggle to explore without uploading any file.

---

## 🛠️ Tech Stack

- **[Groq API](https://console.groq.com)** — Free LLM inference (Llama 3, Qwen3)
- **[Streamlit](https://streamlit.io)** — Web UI, no frontend needed
- **[Python](https://python.org)** — Core language
---

## 📋 What it does

Upload a test results file from JMeter, Playwright, or Selenium and the dashboard automatically produces:

- KPI summary — total tests, passed, failed, pass rate, average response time, P95
- Filterable table with color-coded status, searchable by name, suite, or file
- Failed test details with full error messages
- 5 charts — pass rate by test, response time distribution, result donut, top 10 slowest, box plot spread
- AI analysis that detects failure patterns and gives specific recommendations

Everything runs on the uploaded file with no data stored anywhere.

---

## 🛠️ Supported file formats

| Tool | Format | How to generate |
|---|---|---|
| **JMeter** | `.jtl` (CSV or XML) | Run > Save Results — both formats auto-detected |
| **Playwright** | `.json` | `playwright test --reporter=json > results.json` |
| **Selenium / JUnit** | `.xml` | `pytest --junitxml=results.xml` |

Don't have a file? Enable **Use sample data** in the sidebar — the app loads realistic generated data instantly.

---

## 📈 Charts included

| Chart | What it shows |
|---|---|
| Pass rate by test | Horizontal bar per test/endpoint, color scale red→green |
| Response time distribution | Histogram with Avg, P90, P95 reference lines |
| Overall result | Donut — passed / failed / skipped breakdown |
| Top 10 slowest | Horizontal bar, colored by pass/fail status |
| Response time spread | Box plot per test — reveals outliers and variance |
| HTTP response codes | Bar by status code — JMeter only |

---

## 🤖 AI Analysis

Powered by **Groq API + Llama 3** (free tier, no credit card needed).

The AI receives a compact metrics summary — not the raw file — and returns:

1. Overall assessment of the test run
2. Top failure patterns detected
3. Specific recommendations to improve results

Available in **English** and **Spanish**.

---

## ⚡ Run locally

### 1. Clone the repo

```bash
git clone https://github.com/JoWan1998/qa-results-analyzer
cd qa-results-analyzer
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your Groq API key

Get a free key at [console.groq.com](https://console.groq.com) — no credit card required.

```bash
cp .env.example .env
```

Edit `.env`:

```
GROQ_API_KEY=gsk_your_key_here
```

### 5. Run

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

---

## 📁 Project structure

```
qa-results-analyzer/
├── app.py                  # Streamlit UI — main entry point
├── analyzer.py             # Metrics computation (pass rate, P90, P95, by-label breakdown)
├── ai_summary.py           # Groq API integration — AI analysis and recommendations
├── parsers/
│   ├── jmeter.py           # JMeter .jtl parser — auto-detects CSV and XML formats
│   ├── playwright.py       # Playwright JSON reporter parser
│   ├── junit.py            # Selenium / JUnit XML parser
│   └── sample_data.py      # Realistic sample data generators for demo
├── requirements.txt        # Direct dependencies only
├── .env.example            # API key template
├── .gitignore
└── README.md
```

---

## 📌 Notes

- **JMeter CSV and XML are both supported** — the parser auto-detects the format from the first bytes of the file. No configuration needed.
- **AI analysis is token-efficient** — the app sends a compact metrics summary to the LLM, not the raw file. A full analysis costs ~200–400 input tokens.
- **No data is stored** — uploaded files are held in memory for the session only. Nothing is written to disk or sent anywhere except the metrics summary to Groq.
- **Models with reasoning** (e.g. `qwen3-32b`) may output `<think>` blocks — these are automatically filtered before display.

---

## 👤 Author

**José Orlando Wannan Escobar**
QA Automation Engineer · AI Master's Student · Guatemala

[LinkedIn](https://linkedin.com/in/josewannan1998) · [GitHub](https://github.com/JoWan1998)

---

## 📄 License

[MIT](LICENSE) — free to use, modify and distribute.
