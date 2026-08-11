BEGIN;

ALTER TABLE jobs ADD COLUMN work_schedule TEXT NOT NULL DEFAULT '';
ALTER TABLE jobs ADD COLUMN recurring_weekend_work INTEGER;
ALTER TABLE jobs ADD COLUMN advertised_compensation_currency TEXT;
ALTER TABLE jobs ADD COLUMN advertised_compensation_min INTEGER;
ALTER TABLE jobs ADD COLUMN advertised_compensation_max INTEGER;
ALTER TABLE jobs ADD COLUMN advertised_compensation_basis TEXT;
ALTER TABLE jobs ADD COLUMN strategically_exceptional INTEGER NOT NULL DEFAULT 0;

ALTER TABLE applications ADD COLUMN answer_metadata_json TEXT NOT NULL DEFAULT '{}';
ALTER TABLE applications ADD COLUMN compensation_decision_json TEXT;

COMMIT;
