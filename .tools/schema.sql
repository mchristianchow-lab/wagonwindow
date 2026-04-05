CREATE TABLE IF NOT EXISTS entities (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    vault_path TEXT NOT NULL UNIQUE,
    name TEXT,
    status TEXT DEFAULT 'active',
    created_at TEXT,
    updated_at TEXT,
    last_verified TEXT,
    verified_by TEXT,
    confidence TEXT DEFAULT 'estimated',
    meta TEXT
);

CREATE TABLE IF NOT EXISTS claims (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id TEXT REFERENCES entities(id),
    field TEXT NOT NULL,
    value TEXT,
    previous_value TEXT,
    source_url TEXT,
    source_type TEXT,
    observed_at TEXT NOT NULL,
    expires_at TEXT,
    confidence TEXT,
    superseded_by INTEGER REFERENCES claims(id),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS dependencies (
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    relationship TEXT NOT NULL,
    field TEXT,
    context TEXT,
    discovered_at TEXT,
    PRIMARY KEY (source_id, target_id, relationship)
);

CREATE TABLE IF NOT EXISTS intelligence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    date TEXT NOT NULL,
    entity_id TEXT,
    vector TEXT,
    content TEXT NOT NULL,
    signal TEXT,
    importance TEXT DEFAULT 'normal',
    status TEXT DEFAULT 'active',
    source_file TEXT
);

CREATE TABLE IF NOT EXISTS provenance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id TEXT REFERENCES entities(id),
    action TEXT NOT NULL,
    performed_by TEXT,
    performed_at TEXT NOT NULL,
    details TEXT
);

CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type);
CREATE INDEX IF NOT EXISTS idx_entities_status ON entities(status);
CREATE INDEX IF NOT EXISTS idx_entities_last_verified ON entities(last_verified);
CREATE INDEX IF NOT EXISTS idx_claims_entity ON claims(entity_id);
CREATE INDEX IF NOT EXISTS idx_claims_field ON claims(field);
CREATE INDEX IF NOT EXISTS idx_deps_source ON dependencies(source_id);
CREATE INDEX IF NOT EXISTS idx_deps_target ON dependencies(target_id);
CREATE INDEX IF NOT EXISTS idx_intel_type ON intelligence(type);
CREATE INDEX IF NOT EXISTS idx_intel_date ON intelligence(date);
CREATE INDEX IF NOT EXISTS idx_intel_entity ON intelligence(entity_id);
CREATE INDEX IF NOT EXISTS idx_provenance_entity ON provenance(entity_id);
