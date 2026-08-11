PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS runs (
  run_id TEXT PRIMARY KEY,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  source TEXT NOT NULL,
  mode TEXT NOT NULL,
  discovered_count INTEGER NOT NULL DEFAULT 0,
  normalized_count INTEGER NOT NULL DEFAULT 0,
  duplicate_count INTEGER NOT NULL DEFAULT 0,
  skipped_count INTEGER NOT NULL DEFAULT 0,
  review_count INTEGER NOT NULL DEFAULT 0,
  apply_count INTEGER NOT NULL DEFAULT 0,
  strong_apply_count INTEGER NOT NULL DEFAULT 0,
  prepared_count INTEGER NOT NULL DEFAULT 0,
  submitted_count INTEGER NOT NULL DEFAULT 0,
  errors_json TEXT NOT NULL DEFAULT '[]',
  external_writes_json TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS jobs (
  job_id TEXT PRIMARY KEY,
  source TEXT NOT NULL,
  source_posting_id TEXT,
  original_url TEXT NOT NULL,
  canonical_url TEXT NOT NULL,
  company TEXT NOT NULL,
  actual_employer TEXT,
  destination_company TEXT,
  company_domain TEXT,
  destination_domain TEXT,
  company_origin TEXT NOT NULL,
  company_origin_evidence TEXT NOT NULL DEFAULT '',
  role TEXT NOT NULL,
  location TEXT NOT NULL DEFAULT '',
  remote_policy TEXT NOT NULL DEFAULT '',
  remote_from_ph INTEGER,
  employment_type TEXT NOT NULL DEFAULT '',
  compensation TEXT NOT NULL DEFAULT '',
  description TEXT NOT NULL,
  description_hash TEXT NOT NULL,
  content_fingerprint TEXT NOT NULL,
  active INTEGER NOT NULL,
  posted_at TEXT,
  discovered_at TEXT NOT NULL,
  eligibility_verdict TEXT,
  reason_codes_json TEXT NOT NULL DEFAULT '[]',
  raw_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS jobs_source_posting_unique
  ON jobs(source, source_posting_id) WHERE source_posting_id IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS jobs_canonical_url_unique ON jobs(canonical_url);
CREATE UNIQUE INDEX IF NOT EXISTS jobs_content_fingerprint_unique ON jobs(content_fingerprint);

CREATE TABLE IF NOT EXISTS job_sources (
  source TEXT NOT NULL,
  source_posting_id TEXT NOT NULL DEFAULT '',
  job_id TEXT NOT NULL REFERENCES jobs(job_id),
  url TEXT NOT NULL,
  observed_at TEXT NOT NULL,
  PRIMARY KEY(source, source_posting_id, url)
);

CREATE TABLE IF NOT EXISTS assessments (
  assessment_id TEXT PRIMARY KEY,
  job_id TEXT NOT NULL REFERENCES jobs(job_id),
  fit_score INTEGER,
  verdict TEXT NOT NULL,
  reason_codes_json TEXT NOT NULL,
  rubric_json TEXT,
  assessment_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS assessments_job_id ON assessments(job_id, created_at);

CREATE TABLE IF NOT EXISTS application_drafts (
  draft_id TEXT PRIMARY KEY,
  job_id TEXT NOT NULL REFERENCES jobs(job_id),
  version INTEGER NOT NULL,
  narrative TEXT NOT NULL,
  letter TEXT NOT NULL,
  packet_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE(job_id, version)
);

CREATE TABLE IF NOT EXISTS applications (
  application_id TEXT PRIMARY KEY,
  job_id TEXT NOT NULL UNIQUE REFERENCES jobs(job_id),
  status TEXT NOT NULL,
  application_method TEXT NOT NULL DEFAULT '',
  cv_version TEXT NOT NULL DEFAULT '',
  date_discovered TEXT NOT NULL,
  date_applied TEXT,
  recruiter_contact TEXT NOT NULL DEFAULT '',
  last_response_at TEXT,
  response_type TEXT,
  next_action TEXT NOT NULL DEFAULT '',
  follow_up_date TEXT,
  notes TEXT NOT NULL DEFAULT '',
  submission_evidence_json TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS application_events (
  event_id TEXT PRIMARY KEY,
  application_id TEXT NOT NULL REFERENCES applications(application_id),
  event_type TEXT NOT NULL,
  external_key TEXT,
  payload_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL,
  UNIQUE(application_id, event_type, external_key)
);

CREATE TABLE IF NOT EXISTS email_events (
  message_id TEXT PRIMARY KEY,
  application_id TEXT REFERENCES applications(application_id),
  response_type TEXT NOT NULL,
  confidence REAL NOT NULL,
  ambiguous INTEGER NOT NULL DEFAULT 0,
  candidate_application_ids_json TEXT NOT NULL DEFAULT '[]',
  received_at TEXT NOT NULL,
  metadata_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS schema_migrations (
  version TEXT PRIMARY KEY,
  applied_at TEXT NOT NULL
);
