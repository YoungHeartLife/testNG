CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(100),
  password_hash TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS market_status (
  id SERIAL PRIMARY KEY,
  up_count INT,
  down_count INT,
  limit_up INT,
  limit_down INT,
  market_phase VARCHAR(50),
  risk_level VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ai_signals (
  id SERIAL PRIMARY KEY,
  stock_code VARCHAR(20),
  stock_name VARCHAR(100),
  score FLOAT,
  signal_type VARCHAR(50),
  reasons JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trade_logs (
  id SERIAL PRIMARY KEY,
  stock_code VARCHAR(20),
  action VARCHAR(20),
  reason TEXT,
  profit FLOAT,
  created_at TIMESTAMP DEFAULT NOW()
);
