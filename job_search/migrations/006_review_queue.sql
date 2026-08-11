BEGIN;

CREATE TABLE IF NOT EXISTS review_queue (
  queue_id TEXT PRIMARY KEY,
  job_id TEXT NOT NULL UNIQUE REFERENCES jobs(job_id),
  application_id TEXT REFERENCES applications(application_id),
  source_posting_id TEXT NOT NULL DEFAULT '',
  description_hash TEXT NOT NULL DEFAULT '',
  date_discovered TEXT NOT NULL DEFAULT '',
  last_reviewed TEXT NOT NULL DEFAULT '',
  company TEXT NOT NULL,
  role TEXT NOT NULL,
  source TEXT NOT NULL DEFAULT '',
  ats TEXT NOT NULL DEFAULT '',
  job_url TEXT NOT NULL,
  posted_date TEXT,
  job_age INTEGER,
  fit_score INTEGER,
  verdict TEXT NOT NULL DEFAULT '',
  readiness INTEGER,
  queue_status TEXT NOT NULL CHECK (
    queue_status IN ('PREPARED', 'HELD', 'REVIEW', 'READY TO APPLY', 'CLOSED')
  ),
  hold_review_reason TEXT NOT NULL DEFAULT '',
  next_action TEXT NOT NULL DEFAULT '',
  compensation TEXT NOT NULL DEFAULT '',
  key_matches TEXT NOT NULL DEFAULT '[]',
  material_gaps TEXT NOT NULL DEFAULT '[]',
  prepared_screening_answers TEXT NOT NULL DEFAULT '{}',
  cover_letter TEXT NOT NULL DEFAULT '',
  cv_version TEXT NOT NULL DEFAULT '',
  media_requirement TEXT NOT NULL DEFAULT '',
  source_ats_policy TEXT NOT NULL DEFAULT '',
  re_review_after TEXT,
  notes TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS review_queue_job_url_unique ON review_queue(job_url);
CREATE INDEX IF NOT EXISTS review_queue_due ON review_queue(queue_status, re_review_after);

COMMIT;
