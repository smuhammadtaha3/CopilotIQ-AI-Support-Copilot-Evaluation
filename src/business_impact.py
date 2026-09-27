from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.ingest import build_processed_dataset, load_sample_dataset


def estimate_business_impact(df: pd.DataFrame) -> pd.DataFrame:
    """Compute a simple, explainable business impact summary from category-level metrics."""
    summary = df.groupby("category", dropna=False).agg(
        ticket_count=("customer_message", "size"),
        avg_message_length=("message_length", "mean"),
    ).reset_index()

    summary["minutes_saved_per_ticket"] = 4.0
    summary["team_cost_per_hour"] = 15.0
    summary["monthly_tickets"] = 10000
    summary["monthly_hours_saved"] = summary["ticket_count"] * summary["minutes_saved_per_ticket"] / 60
    summary["monthly_cost_saving_usd"] = summary["monthly_hours_saved"] * summary["team_cost_per_hour"]
    summary["auto_draft_ready"] = summary["avg_message_length"].gt(120)
    return summary.sort_values("monthly_cost_saving_usd", ascending=False)


def main() -> None:
    df = build_processed_dataset(load_sample_dataset())
    impact = estimate_business_impact(df)
    print(impact.to_string(index=False))


if __name__ == "__main__":
    main()
