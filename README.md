# CopilotIQ

CopilotIQ is a prototype for analyzing customer-support conversations and estimating where an AI copilot could help support teams. The current scaffold prepares sample ticket data, summarizes it by category, and displays an illustrative impact table in a local Streamlit dashboard. Multi-model evaluation, PostgreSQL integration, and MLflow tracking are planned, not implemented.

For the full project explanation, current implementation status, file map, caveats, and staged roadmap, see [PROJECT_GUIDE.md](PROJECT_GUIDE.md). The original portfolio vision remains in [CopilotIQ_Project_Roadmap.md](CopilotIQ_Project_Roadmap.md).

## Quick Start (Windows PowerShell)

Run commands from the project root. Using the venv's Python directly avoids conflicts with other Python installations on Windows.

First-time setup:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run the current pipeline and dashboard:

```powershell
.\.venv\Scripts\python.exe src\ingest.py
.\.venv\Scripts\python.exe -m src.business_impact
.\.venv\Scripts\python.exe -m streamlit run dashboard\app.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`. Run tests with:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The current demo does not require API keys or a PostgreSQL server. If no local JSON dataset is supplied, ingestion uses a small built-in synthetic sample. Current impact values are illustrative and should not be presented as measured or scaled business savings.
