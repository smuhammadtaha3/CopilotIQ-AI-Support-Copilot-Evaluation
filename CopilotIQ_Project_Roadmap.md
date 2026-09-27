# CopilotIQ — AI Support Copilot Evaluation & Business Impact Analytics
### A portfolio project built for the TensorOps Junior Data Scientist application

**Owner:** Syed Muhammad Taha
**Role target:** Junior Data Scientist, TensorOps (remote, Pakistan)
**Purpose of this document:** Hand this whole file to a coding agent (Claude Code, Codex, etc.) and it has everything needed to scaffold, build, and finish the project end-to-end — no extra context required.

---

## 0. Why this exact project

TensorOps doesn't build models — it evaluates other people's AI systems (copilots, agents, recommenders) and translates model behavior into **business impact** for clients. Their JD is explicit about this: *"Analyze Performance Data," "Research and Evaluate Models," "Translate Technical to Business," "Create Reports & Presentations."* That is an analyst role wrapped around AI systems, not a model-building role.

So the project is not "I built a chatbot." It's: **"I built an AI customer-support copilot, then did exactly what a TensorOps analyst would do — evaluated it against alternatives, tracked the experiments, quantified the business case, and delivered a client-style report and dashboard."**

This mirrors the discovery-phase workflow TensorOps runs for real clients, and it uses the JD's exact stack: **Python, SQL, Matplotlib/Seaborn, LLMs, LangChain, MLflow, AWS/GCP.**

---

## 1. Stack mapped directly to the job description

| JD requirement | What CopilotIQ does about it |
|---|---|
| Python, Pandas, NumPy | Full pipeline: ingestion, cleaning, feature/metric computation |
| SQL | PostgreSQL schema + analytical queries for ticket volume, category trends, resolution stats |
| Matplotlib, Seaborn | EDA charts + report visuals |
| Tableau / Looker | Public-facing business dashboard (Streamlit as the practical substitute — see Phase 6 note) |
| LLMs, LangChain | The copilot itself is a small LangChain chain generating draft ticket responses (not RAG — a plain prompted chain, honestly scoped) |
| MLflow | Experiment tracking for every model/prompt variant using `mlflow.genai.evaluate()` |
| AWS / GCP | Dataset + evaluation results stored in S3 or GCS; dashboard deployed on a free-tier instance |
| "Analyze performance, evaluate models, translate to business, report" | Phases 5–8 below, end to end |

---

## 2. Dataset

**Bitext Customer Support LLM Chatbot Training Dataset** — public, free, on Hugging Face.
- ~26,872 real customer support utterances
- 28 intent categories (refund, delivery, cancel order, payment issue, etc.)
- Fields: `instruction` (customer message), `intent`, `category`, `response` (ground-truth agent reply)

This is ideal because it gives you a genuine "ground-truth" reply to compare the AI copilot's generated reply against — which is exactly what makes evaluation possible instead of hand-wavy.

```python
from datasets import load_dataset
ds = load_dataset("bitext/Bitext-customer-support-llm-chatbot-training-dataset")
```
(If `datasets` access is restricted in your environment, the same file is mirrored on Kaggle — search "Bitext customer support dataset kaggle.")

---

## 3. Architecture

```
Bitext Dataset (CSV)
      |
[Phase 1] Load into PostgreSQL  --------->  SQL analytics layer
      |
[Phase 2] EDA (Pandas/Matplotlib/Seaborn) -> ticket volume, category mix, text-length, sentiment
      |
[Phase 3] Build the Copilot (LangChain chain: prompt template -> LLM -> draft reply)
      |          also build a 2nd prompt variant (few-shot) to have something to compare
      |
[Phase 4] Multi-model evaluation
      |     - Compare 2-3 LLMs (e.g. GPT-4o-mini, Claude Haiku, a local Llama-3 via Ollama)
      |     - Score each on: relevance, correctness vs ground truth, latency, cost/ticket
      |
[Phase 5] MLflow experiment tracking (mlflow.genai.evaluate, log every run)
      |
[Phase 6] Business impact translation -> cost/time savings model, escalation rate estimate
      |
[Phase 7] Dashboard (Streamlit) + static report charts
      |
[Phase 8] Cloud: data + results in S3/GCS, dashboard deployed to a free-tier host
      |
[Phase 9] Client-style report + one-page executive summary + CV bullet
```

---

## 4. Phase 0 — Environment setup

```bash
mkdir copilotiq && cd copilotiq
python3 -m venv venv && source venv/bin/activate
pip install pandas numpy matplotlib seaborn sqlalchemy psycopg2-binary \
            langchain langchain-openai langchain-anthropic \
            mlflow openai anthropic datasets streamlit boto3 python-dotenv
```
Folder structure:
```
copilotiq/
  data/               # raw + processed dataset
  sql/                # schema.sql, analytics_queries.sql
  notebooks/          # EDA notebooks
  src/
    ingest.py
    copilot.py        # the LangChain chain(s) under test
    evaluate.py        # scoring + MLflow logging
    business_impact.py
  dashboard/
    app.py            # Streamlit
  reports/
    business_report.md
  README.md
```
Set up a free PostgreSQL instance (local via Docker, or a free-tier hosted one like Neon/Supabase) and API keys for at least two LLM providers (a free-tier one is fine — Groq's free tier for Llama-3, plus OpenAI or Anthropic pay-as-you-go with a small budget cap).

---

## 5. Phase 1 — Data engineering & SQL

Load the dataset into Postgres with a schema built for analysis, not just storage:

```sql
CREATE TABLE tickets (
    ticket_id SERIAL PRIMARY KEY,
    customer_message TEXT,
    intent VARCHAR(50),
    category VARCHAR(50),
    ground_truth_response TEXT,
    message_length INT,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE model_runs (
    run_id SERIAL PRIMARY KEY,
    ticket_id INT REFERENCES tickets(ticket_id),
    model_name VARCHAR(50),
    prompt_variant VARCHAR(50),
    generated_response TEXT,
    latency_ms INT,
    cost_usd NUMERIC(10,6),
    relevance_score NUMERIC(4,2),
    correctness_score NUMERIC(4,2)
);
```

Write and save 6-8 analytical SQL queries — these become both dashboard fuel and interview talking points:
- Ticket volume by category/intent
- Average message length by category
- Per-model average relevance/correctness score
- Per-model average latency and cost
- Win-rate: which model scores highest per ticket, grouped by intent
- Categories where every model underperforms (the "hard" cases — this is the business insight TensorOps cares about)

---

## 6. Phase 2 — EDA

Standard but purposeful — this is what a junior analyst is actually judged on:
- Class distribution across the 28 intents (bar chart)
- Message length distribution (histogram) — flags very short/long tickets as an edge case
- Word frequency / top keywords per top 5 intents
- Sentiment pass over customer messages (you already have RoBERTa experience from your Reputation Monitoring Agent project — reuse that fine-tuning skill here for a "customer frustration score" feature, which becomes a business-relevant EDA finding: *"tickets in category X arrive 40% more frustrated on average"*)

Save 4-6 clean Matplotlib/Seaborn figures into `reports/figures/` — these go straight into the final report.

---

## 7. Phase 3 — Build the copilot (honest LangChain scope)

This is **not** a RAG system — don't build or claim retrieval. It's a straightforward prompted chain, which is what most "AI copilot" MVPs actually are:

```python
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

prompt = PromptTemplate.from_template(
    "You are a customer support agent. Category: {category}\n"
    "Customer message: {message}\n"
    "Write a concise, helpful reply."
)
chain = prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
```

Build **two prompt variants** so you have a real comparison to run, not a single system with nothing to benchmark against:
1. **v1 — zero-shot**: instruction only (above)
2. **v2 — few-shot**: same instruction + 2-3 example Q/A pairs pulled from the dataset's `ground_truth_response` field

---

## 8. Phase 4 — Multi-model evaluation

Run both prompt variants across 2-3 LLMs on a sampled subset (300-500 tickets is plenty — don't burn API budget on the full 26k):

| Model | Access |
|---|---|
| GPT-4o-mini | OpenAI API (cheap, fast baseline) |
| Claude Haiku | Anthropic API |
| Llama-3-8B | Free via Groq API or local via Ollama |

For each (ticket, model, prompt variant) triple, capture: generated response, latency, cost, and a relevance/correctness score.

---

## 9. Phase 5 — MLflow experiment tracking

This is the JD's MLflow line, done properly with 2026's GenAI evaluation API rather than the old classic-ML-only workflow:

```python
import mlflow

mlflow.set_experiment("copilotiq-support-response-eval")

with mlflow.start_run(run_name="gpt4o-mini_fewshot"):
    results = mlflow.genai.evaluate(
        predict_fn=my_chain_predict_fn,
        data=eval_dataset,          # ticket, ground_truth_response
        scorers=["correctness", "relevance_to_query"],
    )
    mlflow.log_metric("avg_latency_ms", avg_latency)
    mlflow.log_metric("avg_cost_usd", avg_cost)
```

Run this once per (model x prompt variant) combination — 4-6 runs total. Open the MLflow UI locally and screenshot the comparison table/chart for the report; this screenshot is one of the strongest CV/portfolio artifacts because it's the exact tool the JD names.

---

## 10. Phase 6 — Business impact translation

This is the part that actually differentiates a "junior data scientist" candidate from someone who just fine-tuned a model. Convert the technical metrics into a business case:

- Estimate **average human agent time per ticket** (research-backed assumption, cite a source, ~4-6 minutes is typical for simple categories)
- Estimate **copilot draft-assist time** (near-instant generation + ~1 min human review/edit)
- Compute **potential time savings %** per category, split into "safe to auto-draft" vs "needs full human handling" based on your correctness scores (e.g., only auto-draft categories where correctness > 0.85)
- Translate into a **projected monthly cost saving** for a hypothetical support team size (state your assumption clearly — e.g., "for a team handling 10,000 tickets/month at $15/hr loaded cost")
- Flag the **categories where AI hurts more than helps** — this "know its limits" framing is exactly the business judgment TensorOps wants to see, and mirrors your own reputation-agent project's 65% turnaround framing

Put this in a small `business_impact.py` script that outputs a clean summary table, not just prose — this becomes a dashboard tile and a report table.

---

## 11. Phase 7 — Dashboard

Build the dashboard in **Streamlit** (fast, free, Python-native — the practical stand-in for Tableau/Looker when you don't have a paid seat; say so honestly in your README rather than implying it's Tableau).

Tabs/sections:
1. **Overview** — ticket volume, category mix
2. **Model comparison** — correctness/relevance/latency/cost per model, side by side
3. **Business impact** — the time/cost savings table from Phase 6
4. **Hard cases** — categories where models struggle, with example failures

If you later get access to Tableau Public, exporting the same aggregated CSVs into a Tableau Public dashboard is a quick add-on and lets you genuinely list Tableau too.

---

## 12. Phase 8 — Cloud (AWS/GCP)

Keep this simple and free-tier-safe:
- Push `data/` and `reports/figures/` to an **S3 bucket** (or GCS bucket) — this alone is enough to genuinely claim "used AWS/GCP for data storage"
- Deploy the Streamlit dashboard on a free-tier **EC2 t3.micro** (750 hrs/month free) or **Cloud Run** (GCP's pay-per-use free quota is generous for a low-traffic demo)
- Document the exact deploy steps in the README so it's reproducible and demonstrable in an interview

Set a AWS Budget alert at $1 before you start — free tier is easy to exceed by accident if you forget to stop an instance.

---

## 13. Phase 9 — Reporting (the deliverable that actually gets you the interview)

Produce two documents that mirror what TensorOps analysts deliver to clients:

1. **`business_report.md`** (2-3 pages) — written exactly like a client deliverable:
   - Executive summary (3 sentences, cost-savings number up front)
   - What was evaluated and why
   - Key findings (model comparison table + business impact table)
   - Recommendation (which model/prompt to deploy, where AI should NOT be trusted yet)
   - Appendix: methodology, MLflow screenshot, dashboard link
2. **One-page executive summary** (can be a simple PDF or Canva one-pager) — the thing you'd actually attach to a job application as a work sample

---

## 14. Phase 10 — Packaging for your CV and applications

- GitHub repo, clean README with the architecture diagram from Section 3, screenshots of the dashboard and MLflow UI, and a "Business Impact" section up top (recruiters skim READMEs top-down)
- Once built, fill in your actual numbers into a resume bullet using your usual CAR/STAR one-liner format, e.g.:
  *"Built and evaluated a multi-LLM customer-support copilot (LangChain, MLflow, PostgreSQL) that solves [X problem], which reduces projected ticket handling time by [Y%] while flagging categories where AI assistance underperforms."*
  — fill in X/Y once you have real numbers; don't estimate them now.
- This project directly answers the interview question "tell me about a project where you evaluated an AI system's business impact," which is the exact shape of question this JD will ask.

---

## 15. Suggested build order / time budget

| Week | Focus |
|---|---|
| 1 | Phases 0-2 (setup, data, SQL, EDA) |
| 2 | Phases 3-5 (copilot chains, multi-model eval, MLflow) |
| 3 | Phases 6-8 (business impact, dashboard, cloud deploy) |
| 4 | Phase 9-10 (report, packaging, CV bullet, apply) |

Hand this file to Claude Code (or another agent) one phase at a time — start with "read CopilotIQ_Project_Roadmap.md, set up Phase 0 and Phase 1" rather than asking for the whole thing at once, so you can review and steer between phases.
