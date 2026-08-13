BEGIN;

ALTER TABLE review_queue ADD COLUMN expires_at TEXT;
ALTER TABLE review_queue ADD COLUMN last_verified_at TEXT;

CREATE TABLE run_outcomes (
  run_id TEXT NOT NULL REFERENCES runs(run_id),
  job_id TEXT NOT NULL,
  outcome TEXT NOT NULL,
  occurrence_key TEXT NOT NULL DEFAULT '',
  payload_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL,
  PRIMARY KEY(run_id, job_id, outcome, occurrence_key)
);

CREATE INDEX run_outcomes_run ON run_outcomes(run_id, outcome);
CREATE INDEX review_queue_expiry ON review_queue(queue_status, expires_at);

COMMIT;
