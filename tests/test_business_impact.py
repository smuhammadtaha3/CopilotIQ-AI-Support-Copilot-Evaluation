from src.business_impact import estimate_business_impact


def test_estimate_business_impact_generates_summary_table():
    sample = [
        {
            "instruction": "I want a refund on an order.",
            "intent": "refund",
            "category": "billing",
            "response": "I can help with that.",
        },
        {
            "instruction": "My package is late.",
            "intent": "delivery",
            "category": "shipping",
            "response": "I can check the tracking.",
        },
    ]

    df = __import__("pandas").DataFrame(sample)
    df["message_length"] = df["instruction"].str.len()
    df["customer_message"] = df["instruction"]
    df["ground_truth_response"] = df["response"]

    impact = estimate_business_impact(df)

    assert list(impact.columns)[:3] == ["category", "ticket_count", "avg_message_length"]
    assert impact["ticket_count"].sum() == 2
    assert "monthly_cost_saving_usd" in impact.columns
