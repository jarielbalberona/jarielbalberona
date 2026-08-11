BEGIN;

ALTER TABLE jobs ADD COLUMN advertised_compensation_monthly_php_min INTEGER;
ALTER TABLE jobs ADD COLUMN advertised_compensation_monthly_php_max INTEGER;
ALTER TABLE jobs ADD COLUMN advertised_compensation_exchange_rate_to_php REAL;
ALTER TABLE jobs ADD COLUMN advertised_compensation_conversion_date TEXT;

COMMIT;
