# CopilotIQ Project Guide

## At A Glance

**CopilotIQ is a prototype for analyzing customer-support conversations and estimating where an AI copilot could help support teams.** Its current runnable version loads local or sample ticket data, standardizes fields, calculates simple category-level workload estimates, and displays the results in a Streamlit dashboard.

The larger goal is to compare AI-generated reply drafts across models and prompts, measure quality and operating cost, and turn those results into a defensible business recommendation. Those model-evaluation and database features are roadmap items; they are not implemented in the current scaffold.

## Explain It To Anyone

### Nontechnical explanation

Customer-support teams receive many similar questions. CopilotIQ is a small analysis tool that organizes example support messages by topic and estimates how much agent time might be saved if an AI assistant helped draft replies. It also provides a dashboard for reviewing the summary. The current demo uses a tiny synthetic sample unless a local dataset is supplied, so its savings numbers are examples, not evidence of real-world savings.

### Technical explanation

CopilotIQ is a Python data-processing prototype. `src/ingest.py` loads JSON records (or a built-in fallback sample), maps the source fields into an analysis-friendly pandas DataFrame, derives message length, and writes a processed CSV. `src/business_impact.py` aggregates the prepared data by category and applies configurable-in-code time and labor-cost assumptions. `dashboard/app.py` runs the same preparation and displays ticket counts, category counts, and the impact table with Streamlit. PostgreSQL DDL and analytics queries are present as design artifacts, but the application does not currently connect to a database or execute those queries.

### Short presentation version

> CopilotIQ is a customer-support AI evaluation project. The current prototype prepares support-ticket data, summarizes it by category, and shows an illustrative time-and-cost impact in a dashboard. The next stages are to load a real dataset, connect the SQL layer, compare model and prompt variants against reference replies, and report measured quality, latency, and cost before making any deployment recommendation.

## Problem And Purpose

Support leaders need more than a fluent AI response. They need evidence about whether draft replies are useful, correct, fast, affordable, and appropriate for particular ticket types. CopilotIQ is intended to make that evaluation workflow visible:

1. Prepare representative support-ticket data.
2. Compare candidate AI replies with reference answers.
3. Measure quality, latency, and cost consistently.
4. Identify ticket categories where AI assistance is helpful or risky.
5. Translate measured results into a clearly qualified business case.
6. Present findings in a dashboard and concise report.

The project is an evaluation and analytics tool, not a production customer-service chatbot. It does not currently send replies to customers.

## Current Workflow

```text
Local JSON dataset, if supplied
        or
Built-in synthetic fallback sample
        |
        v
src/ingest.py
Load records, normalize fields, derive message length
        |
        +----> data/processed/customer_support_tickets.csv
        |
        v
src/business_impact.py
Aggregate current sample by category and apply illustrative assumptions
        |
        v
dashboard/app.py
Show sample counts and the impact table in Streamlit
```

The dashboard and impact script currently load and process the input DataFrame directly. The generated CSV is a useful pipeline output, but the dashboard does not currently query that CSV or a database.

## What Works Today

| Capability | Current implementation | Important qualification |
|---|---|---|
| Input loading | Reads `data/raw/bitext_customer_support_sample.json` when present; otherwise uses three built-in sample records | The project does not download the Bitext dataset automatically. The fallback is synthetic, not a real evaluation dataset. |
| Data preparation | Maps `instruction` to `customer_message`, `response` to `ground_truth_response`, and calculates character count as `message_length` | This is basic field preparation, not full data validation or text analysis. |
| CSV output | Writes `data/processed/customer_support_tickets.csv` | Produced by running the ingestion script. |
| Category summary | Counts sample tickets and averages message length by category | It does not measure model correctness or actual agent outcomes. |
| Streamlit dashboard | Displays sample ticket count, category count, and the impact table | It is a starter dashboard, not a complete model comparison/reporting product. |
| SQL artifacts | Defines `tickets` and `model_runs` tables and includes example aggregate queries | They are not connected to the Python application and have not been run against PostgreSQL. |
| Regression test | Checks basic output columns, ticket count, and a savings column | The test does not validate real-world savings assumptions or model evaluation. |

## Important: Interpreting The Impact Numbers

The present impact function uses hard-coded assumptions of **4 minutes saved per ticket** and **$15 per hour**. It groups by category and calculates hours and dollars from the number of records in the loaded sample. Although the output includes a `monthly_tickets` field set to 10,000, that field is currently **not used in the savings formulas**. Therefore, the output is not a correctly scaled forecast for 10,000 monthly tickets.

The `auto_draft_ready` field currently means only that average customer-message length is greater than 120 characters. It is not based on answer quality, correctness, risk, or a human review. Do not use it to decide whether a real ticket can be automated.

Treat all current impact values as **illustrative prototype output**, not measured savings or a deployment recommendation. A future business case should state its assumptions, use real monthly ticket volumes, and qualify savings by measured quality and human-review requirements.

## Data Contract

The current loader expects a JSON array of records with these keys:

| Input key | Meaning | Prepared output |
|---|---|---|
| `instruction` | Customer's message | `customer_message` |
| `intent` | Specific request type, such as refund or delivery | `intent` |
| `category` | Broader support topic, such as billing or shipping | `category` |
| `response` | Reference or ground-truth agent response | `ground_truth_response` |

The processed CSV also contains `message_length`, which is the number of characters in `customer_message`. If a local dataset is supplied, place it at `data/raw/bitext_customer_support_sample.json` or pass a path when calling the loader from Python. The built-in sample is used if the default file does not exist.

## File Map: What, Where, And Why

| Path | What it contains | Why it is used |
|---|---|---|
| `CopilotIQ_Project_Roadmap.md` | Original, detailed project vision and proposed implementation phases | Source for the target capabilities and portfolio direction; it describes more than the current code implements. |
| `README.md` | Short entry point, setup, and run commands | Lets a developer quickly install and run the existing scaffold. |
| `PROJECT_GUIDE.md` | This project explanation, status, file map, and roadmap | Helps both technical and nontechnical readers understand the project and its limits. |
| `src/ingest.py` | JSON/fallback loading, field preparation, CSV export | Establishes the input-to-processed-data path. |
| `src/business_impact.py` | Category summary and current illustrative impact calculation | Demonstrates how technical data could be translated into operational estimates. |
| `dashboard/app.py` | Streamlit user interface | Makes the current summary easier to inspect than console output alone. |
| `data/raw/` | Location intended for source data | Keeps original input separate from derived data. |
| `data/processed/` | Generated, analysis-ready CSV output | Stores the result of the ingestion step. |
| `sql/schema.sql` | PostgreSQL table definitions for tickets and model runs | Defines a future persistence model for input tickets and evaluated AI responses. |
| `sql/analytics_queries.sql` | Example SQL aggregations | Shows intended analyses such as category volume and per-model quality/cost. |
| `tests/test_business_impact.py` | Focused test for the summary table | Guards basic behavior as the impact logic evolves. |
| `requirements.txt` | Required runtime libraries and commented optional future packages | Separates dependencies needed for the current scaffold from later integrations. |
| `.env.example` | Placeholder API, database, MLflow, and AWS settings | Documents configuration expected by possible future integrations; current code does not consume these settings. |
| `reports/figures/` | Intended destination for generated report figures | Reserved for later EDA/report outputs; currently empty. |
| `notebooks/` | Reserved for exploratory analysis notebooks | Keeps interactive EDA separate from reusable pipeline scripts. |

## Technology Choices

| Technology | Where it appears | Why it is used or planned |
|---|---|---|
| Python 3.11 | Local runtime | Stable baseline for the current Windows environment and scientific Python packages. |
| pandas | `src/ingest.py`, `src/business_impact.py` | Loads tabular records, derives fields, groups categories, and formats summaries. |
| Streamlit | `dashboard/app.py` | Provides a local, Python-native dashboard without requiring a separate frontend stack. |
| pytest | `tests/` | Runs automated checks on reusable analytics logic. |
| PostgreSQL / SQLAlchemy / psycopg2 | SQL design and dependencies | Intended for durable storage and repeatable SQL analysis; database integration is not implemented yet. |
| Matplotlib / Seaborn | Dependencies and roadmap | Intended for exploratory charts and static report figures; no chart pipeline is implemented yet. |
| LangChain and model-provider SDKs | Optional packages in `requirements.txt` and roadmap | Intended for generating replies with multiple models and prompt variants; no model calls exist in the current scaffold. |
| MLflow | Roadmap and `.env.example` | Intended to track evaluation experiments; not connected or used by current code. |
| AWS S3 / GCP storage | Roadmap and `.env.example` | Optional future storage/deployment path; not implemented. |

## Run It On Windows

Run these commands from the repository root in PowerShell. Calling Python through `.venv` avoids ambiguity when more than one Python installation is on `PATH`.

### First-time setup

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Run the current pipeline

```powershell
.\.venv\Scripts\python.exe src\ingest.py
.\.venv\Scripts\python.exe -m src.business_impact
.\.venv\Scripts\python.exe -m streamlit run dashboard\app.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`. Leave that terminal running while using the dashboard. `business_impact` is launched with `-m` because it imports from the `src` package. Streamlit is launched as a Python module so the command works even if the `streamlit` executable is not found by PowerShell.

### Run tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

No PostgreSQL server or API key is required for the current local demo. The `.env` file is not required for the implemented pipeline.

## Roadmap

The stages below build from the working prototype toward the original project vision. Keep the first evaluation small, reproducible, and budget-conscious.

### Stage 1: Make data ingestion reliable

- Select and document a real customer-support dataset and its usage terms.
- Support the dataset's actual file format and normalize it into the existing data contract.
- Validate required fields, missing values, duplicate rows, and category/intent consistency.
- Add tests for real-shaped input and malformed input.
- Record source, row count, and processing date with each export.

**Done when:** A clean command reproducibly creates the processed dataset from documented source data, with validation errors that explain bad input.

### Stage 2: Complete exploratory analysis and SQL storage

- Add EDA for category/intent distribution, message lengths, and useful text patterns.
- Save readable plots under `reports/figures/`.
- Decide whether PostgreSQL is required for the portfolio demo; if so, implement connection configuration and ticket loading.
- Run the saved queries against populated tables and test expected results.

**Done when:** EDA outputs and SQL metrics can be regenerated and their source data is clear.

### Stage 3: Build a controlled copilot baseline

- Add a model adapter that generates a draft response from a ticket and category.
- Store provider keys outside source control; make model calls opt-in.
- Implement at least two documented prompt variants, such as zero-shot and few-shot.
- Keep reference answers separate from generated answers to avoid accidental leakage into prompts or scoring.

**Done when:** A small, reproducible sample can be run against a configured model and saved with model name, prompt version, response, and timestamp.

### Stage 4: Evaluate models and prompts

- Start with a small fixed ticket sample to control latency and API cost.
- Record response quality, latency, and cost per ticket.
- Define correctness and relevance scoring criteria; validate automated scores with human review.
- Analyze performance by category and inspect failure cases, not only overall averages.

**Done when:** A repeatable evaluation can compare model/prompt combinations on the same tickets and make uncertainty and scoring limits visible.

### Stage 5: Track experiments

- Integrate MLflow after the evaluation data shape and metrics are stable.
- Log model, prompt version, dataset/sample version, metrics, and artifacts for each run.
- Provide a local experiment-viewing workflow.

**Done when:** A reader can reproduce and compare runs without relying on undocumented terminal history.

### Stage 6: Correct and qualify the business-impact model

- Replace hard-coded values with explicit configurable inputs, including monthly eligible volume, review time, agent cost, and adoption rate.
- Separate observed metrics from assumptions and scenario estimates.
- Base automation or draft-assist recommendations on quality and risk evidence, not message length.
- Show conservative, expected, and optimistic scenarios where appropriate.

**Done when:** Each displayed savings estimate can be traced to documented assumptions and measured evaluation results.

### Stage 7: Expand the dashboard and report

- Add model/prompt comparison, category filters, cost/latency/quality views, and representative hard cases.
- Add download/export options for aggregated results and figures.
- Write a client-style report with methodology, findings, caveats, recommendation, and next steps.

**Done when:** A stakeholder can understand what was tested, what the evidence says, and what should happen next without reading the source code.

### Stage 8: Package and optionally deploy

- Document reproducible setup and add screenshots or a short demo.
- Add cloud storage or hosting only if it improves access to the deliverable; set budget alerts and avoid storing secrets or sensitive customer text unnecessarily.
- Keep local execution available as the baseline.

**Done when:** Another person can run or inspect the project from the docs, and any hosted deployment has clear cost, privacy, and security boundaries.

## Suggested Measures For A Future Evaluation

- **Correctness:** Does the draft accurately address the customer's issue and avoid unsupported claims?
- **Relevance:** Does the draft respond to the actual request and stay on topic?
- **Latency:** How long does generation take per ticket?
- **Cost per ticket:** What is the model/API cost for a draft?
- **Human edit or acceptance rate:** How often does an agent use the draft with little or no change?
- **Escalation or risk rate:** How often should the ticket be routed to a human specialist?
- **Business impact:** What net time or cost change remains after review time, failure handling, and adoption are included?

These metrics are proposed evaluation targets; they are not currently produced by the code.

## Glossary

- **Ground-truth/reference response:** A known support reply supplied with a dataset, used as a comparison reference. It is not automatically a perfect answer or a complete definition of correctness.
- **Prompt variant:** A distinct instruction format given to a model, for example with or without examples.
- **Model run:** One model generating a response for a ticket under a particular prompt and configuration.
- **Latency:** The elapsed time required to produce a response.
- **Business-impact estimate:** A scenario calculation based on measured results and stated operational assumptions; it is not the same as realized savings.
- **MLflow:** A tool planned for recording and comparing model-evaluation experiments.
