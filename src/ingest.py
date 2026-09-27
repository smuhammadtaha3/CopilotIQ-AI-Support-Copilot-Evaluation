from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"


def load_sample_dataset(path: str | Path | None = None) -> pd.DataFrame:
    """Load the Bitext dataset if available, otherwise return a synthetic sample."""
    dataset_path = Path(path) if path else RAW_DIR / "bitext_customer_support_sample.json"

    if dataset_path.exists():
        with open(dataset_path, "r", encoding="utf-8") as f:
            rows = json.load(f)
        return pd.DataFrame(rows)

    sample_rows = [
        {
            "instruction": "I was charged twice for my order and need a refund.",
            "intent": "refund",
            "category": "billing",
            "response": "I am sorry about the duplicate charge. I will review the payment and issue a refund if eligible.",
        },
        {
            "instruction": "My package has not arrived after 10 days.",
            "intent": "delivery",
            "category": "shipping",
            "response": "I apologize for the delay. I can check the carrier status and help with the delivery details.",
        },
        {
            "instruction": "I want to cancel my subscription before renewal.",
            "intent": "cancel_order",
            "category": "account",
            "response": "I can help cancel the subscription and confirm the renewal date before processing the request.",
        },
    ]

    return pd.DataFrame(sample_rows)


def build_processed_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Add lightweight derived fields used by later analytics and business-impact steps."""
    processed = df.copy()
    processed["customer_message"] = processed["instruction"].fillna("")
    processed["ground_truth_response"] = processed["response"].fillna("")
    processed["message_length"] = processed["customer_message"].str.len()
    return processed[["customer_message", "intent", "category", "ground_truth_response", "message_length"]]


def save_processed_dataset(df: pd.DataFrame, output_path: str | Path | None = None) -> Path:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    target = Path(output_path) if output_path else PROCESSED_DIR / "customer_support_tickets.csv"
    df.to_csv(target, index=False)
    return target


def main() -> None:
    df = load_sample_dataset()
    processed_df = build_processed_dataset(df)
    saved_path = save_processed_dataset(processed_df)
    print(f"Processed dataset saved to {saved_path}")


if __name__ == "__main__":
    main()
