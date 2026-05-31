-- schema.sql — Initial SQLite schema for Risk Assessment Platform
-- Tables: assets, threats, assessments, compliance_status

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    name TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    value_usd REAL NOT NULL,
    description TEXT,
    software TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS threats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    category TEXT,
    probability REAL NOT NULL CHECK(probability BETWEEN 0 AND 1),
    vulnerability_score INTEGER NOT NULL CHECK(vulnerability_score BETWEEN 1 AND 5),
    mitigation_effectiveness REAL NOT NULL CHECK(mitigation_effectiveness BETWEEN 0 AND 1),
    aro REAL NOT NULL,
    exposure_factor REAL NOT NULL CHECK(exposure_factor BETWEEN 0 AND 1),
    uncertainty REAL DEFAULT 0.1 CHECK(uncertainty BETWEEN 0 AND 1),
    threat_level INTEGER DEFAULT 3 CHECK(threat_level BETWEEN 1 AND 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    results_json TEXT NOT NULL,
    llm_recommendations TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS compliance_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    control_id TEXT NOT NULL,
    control_name TEXT NOT NULL,
    status TEXT CHECK(status IN ('implemented', 'partial', 'not_implemented')),
    notes TEXT,
    UNIQUE(session_id, control_id)
);

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    message TEXT NOT NULL,
    severity TEXT DEFAULT 'info',
    read_flag INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_assets_session ON assets(session_id);
CREATE INDEX IF NOT EXISTS idx_threats_asset ON threats(asset_id);
CREATE INDEX IF NOT EXISTS idx_assessments_session ON assessments(session_id);
CREATE INDEX IF NOT EXISTS idx_compliance_session ON compliance_status(session_id);
