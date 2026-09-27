CREATE TABLE IF NOT EXISTS tickets (
    ticket_id SERIAL PRIMARY KEY,
    customer_message TEXT,
    intent VARCHAR(100),
    category VARCHAR(100),
    ground_truth_response TEXT,
    message_length INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS model_runs (
    run_id SERIAL PRIMARY KEY,
    ticket_id INT REFERENCES tickets(ticket_id),
    model_name VARCHAR(100),
    prompt_variant VARCHAR(100),
    generated_response TEXT,
    latency_ms INT,
    cost_usd NUMERIC(10, 6),
    relevance_score NUMERIC(4, 2),
    correctness_score NUMERIC(4, 2)
);
