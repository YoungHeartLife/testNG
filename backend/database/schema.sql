CREATE TABLE IF NOT EXISTS scan_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  started_at TEXT NOT NULL,
  finished_at TEXT NOT NULL,
  data_source TEXT NOT NULL,
  status TEXT NOT NULL,
  message TEXT
);

CREATE TABLE IF NOT EXISTS market_status (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  scan_run_id INTEGER NOT NULL,
  market_status TEXT NOT NULL,
  up_count INTEGER NOT NULL,
  down_count INTEGER NOT NULL,
  flat_count INTEGER NOT NULL,
  limit_up INTEGER NOT NULL,
  limit_down INTEGER NOT NULL,
  broken_limit_up INTEGER NOT NULL,
  broken_limit_rate REAL NOT NULL,
  risk_level TEXT NOT NULL,
  allow_buy INTEGER NOT NULL,
  prompt TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(scan_run_id) REFERENCES scan_runs(id)
);

CREATE TABLE IF NOT EXISTS crawled_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  scan_run_id INTEGER NOT NULL,
  source TEXT NOT NULL,
  title TEXT NOT NULL,
  url TEXT NOT NULL,
  summary TEXT,
  published_at TEXT,
  crawled_at TEXT NOT NULL,
  FOREIGN KEY(scan_run_id) REFERENCES scan_runs(id)
);

CREATE TABLE IF NOT EXISTS ai_analysis (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  scan_run_id INTEGER NOT NULL,
  provider TEXT NOT NULL,
  model TEXT NOT NULL,
  summary TEXT NOT NULL,
  sentiment TEXT NOT NULL,
  risk_score INTEGER NOT NULL,
  suggested_action TEXT NOT NULL,
  key_points_json TEXT NOT NULL,
  raw_response TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY(scan_run_id) REFERENCES scan_runs(id)
);

CREATE TABLE IF NOT EXISTS ai_signals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  scan_run_id INTEGER NOT NULL,
  stock_code TEXT NOT NULL,
  stock_name TEXT NOT NULL,
  score REAL NOT NULL,
  signal_type TEXT NOT NULL,
  factors_json TEXT NOT NULL,
  explanation TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(scan_run_id) REFERENCES scan_runs(id)
);

CREATE TABLE IF NOT EXISTS strategy_decisions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  scan_run_id INTEGER NOT NULL,
  action TEXT NOT NULL,
  allow_buy INTEGER NOT NULL,
  position TEXT NOT NULL,
  risk_score INTEGER NOT NULL,
  reasons_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(scan_run_id) REFERENCES scan_runs(id)
);

CREATE TABLE IF NOT EXISTS notifications (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  scan_run_id INTEGER NOT NULL,
  channel TEXT NOT NULL,
  status TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  error TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY(scan_run_id) REFERENCES scan_runs(id)
);

CREATE TABLE IF NOT EXISTS trade_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  stock_code TEXT NOT NULL,
  action TEXT NOT NULL,
  reason TEXT NOT NULL,
  profit REAL DEFAULT 0,
  created_at TEXT NOT NULL
);
