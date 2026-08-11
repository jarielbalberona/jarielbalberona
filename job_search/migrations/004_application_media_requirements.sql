BEGIN;

CREATE TABLE IF NOT EXISTS application_media_requirements (
  job_id TEXT PRIMARY KEY REFERENCES jobs(job_id),
  application_url TEXT NOT NULL DEFAULT '',
  ats TEXT NOT NULL DEFAULT '',
  video_requirement TEXT NOT NULL CHECK (
    video_requirement IN ('REQUIRED', 'OPTIONAL', 'NOT_REQUIRED', 'UNKNOWN_NOT_INSPECTED', 'INACCESSIBLE')
  ),
  photo_requirement TEXT NOT NULL CHECK (
    photo_requirement IN ('REQUIRED', 'OPTIONAL', 'NOT_REQUIRED', 'UNKNOWN_NOT_INSPECTED', 'INACCESSIBLE')
  ),
  video_prompt TEXT NOT NULL DEFAULT '',
  video_duration TEXT NOT NULL DEFAULT '',
  video_method TEXT NOT NULL DEFAULT '',
  evidence_json TEXT NOT NULL DEFAULT '{}',
  inspected_at TEXT,
  updated_at TEXT NOT NULL
);

COMMIT;
