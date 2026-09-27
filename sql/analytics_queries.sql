-- Ticket volume by category
SELECT category, COUNT(*) AS ticket_count
FROM tickets
GROUP BY category
ORDER BY ticket_count DESC;

-- Average message length by category
SELECT category, AVG(message_length) AS avg_message_length
FROM tickets
GROUP BY category
ORDER BY avg_message_length DESC;

-- Per-model average correctness and relevance
SELECT model_name, AVG(correctness_score) AS avg_correctness, AVG(relevance_score) AS avg_relevance
FROM model_runs
GROUP BY model_name
ORDER BY avg_correctness DESC;

-- Per-model average latency and cost
SELECT model_name, AVG(latency_ms) AS avg_latency_ms, AVG(cost_usd) AS avg_cost_usd
FROM model_runs
GROUP BY model_name
ORDER BY avg_cost_usd ASC;

-- Categories with the lowest aggregate model performance
SELECT t.category, AVG(m.correctness_score) AS avg_correctness
FROM tickets t
LEFT JOIN model_runs m ON t.ticket_id = m.ticket_id
GROUP BY t.category
ORDER BY avg_correctness ASC;
