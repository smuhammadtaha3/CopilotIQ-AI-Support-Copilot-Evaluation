from __future__ import annotations

import streamlit as st

from src.business_impact import estimate_business_impact
from src.ingest import build_processed_dataset, load_sample_dataset


st.set_page_config(page_title="CopilotIQ Dashboard", page_icon="📊")
st.title("CopilotIQ — AI Support Copilot Evaluation")

sample_df = build_processed_dataset(load_sample_dataset())
impact = estimate_business_impact(sample_df)

with st.container():
    st.subheader("Overview")
    st.metric("Sample tickets", len(sample_df))
    st.metric("Categories analyzed", sample_df["category"].nunique())

st.subheader("Business impact")
st.dataframe(impact, use_container_width=True)

st.subheader("Hard cases")
for _, row in impact.head(3).iterrows():
    st.write(f"- {row['category']}: {int(row['ticket_count'])} tickets, projected monthly savings ${row['monthly_cost_saving_usd']:.2f}")
