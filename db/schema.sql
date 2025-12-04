CREATE TABLE banks (
    bank_id SERIAL PRIMARY KEY,
    bank_name VARCHAR(255) NOT NULL,
    app_name VARCHAR(255)
);

CREATE TABLE reviews (
    review_id BIGSERIAL PRIMARY KEY,
    bank_id INTEGER REFERENCES banks(bank_id),
    review_text TEXT,
    rating INTEGER,
    review_date DATE,
    sentiment_label VARCHAR(50),
    sentiment_score FLOAT,
    source VARCHAR(50),
    UNIQUE (bank_id, review_text, review_date)
);
