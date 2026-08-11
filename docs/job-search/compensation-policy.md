# Compensation policy

Machine-readable thresholds live in `job_search/policy/compensation_policy.json`. This document defines how to use them. The default basis is PHP gross monthly compensation.

## Employee thresholds

```yaml
hard_minimum_monthly_php: 160000
preferred_minimum_monthly_php: 180000
target_range_monthly_php:
  min: 200000
  max: 250000
```

- Below PHP 160,000: normally `SKIP / COMPENSATION_BELOW_MINIMUM`.
- PHP 160,000-179,999: `REVIEW / COMPENSATION_REVIEW`.
- PHP 180,000-199,999: acceptable depending on the role.
- PHP 200,000-250,000: `COMPENSATION_TARGET_MATCH`.
- Above PHP 250,000: positive; never reject for being above target.

## Contractor thresholds

Apply these to contractor, independent-contractor, consultant, freelance, B2B, and equivalent full-time non-employee arrangements.

```yaml
hard_minimum_monthly_php: 200000
preferred_minimum_monthly_php: 220000
target_range_monthly_php:
  min: 220000
  max: 300000
```

- Below PHP 200,000: normally `SKIP / COMPENSATION_BELOW_MINIMUM`.
- PHP 200,000-219,999: `REVIEW / COMPENSATION_REVIEW`.
- PHP 220,000-300,000: `COMPENSATION_TARGET_MATCH`.
- Above PHP 300,000: positive.

Do not penalize an otherwise suitable full-time role merely because it uses a legitimate non-employee structure.

## High alignment

For AI-native product engineering, agentic AI, coding agents, AI platforms, developer tooling or productivity, Staff-level hands-on engineering, or broad product/platform architecture ownership:

```yaml
preferred_minimum_monthly_php: 230000
stretch_target_monthly_php: 300000
```

There is no compensation ceiling.

## Expected-compensation answers

Expected compensation is a canonical policy decision, not an unresolved applicant fact. Select it autonomously from engagement type, seniority, technical and career fit, AI alignment, ownership, advertised range, benefits, contract risk, working hours, and overall application strength.

Default single-value anchors when no better employer evidence exists:

- Standard Senior employee: PHP 220,000 monthly.
- Strong Senior AI-native employee: PHP 230,000-250,000 monthly; default PHP 240,000.
- Highly aligned Staff or agentic employee: PHP 250,000-300,000 monthly; default PHP 275,000.
- Standard strong contractor: PHP 250,000 monthly.
- Highly aligned AI-native contractor: PHP 275,000 monthly; reasonable range PHP 250,000-300,000.

Do not mechanically choose the minimum or widest range. If the employer publishes a range that fully meets policy, position a strong candidate around its middle-to-upper end. A partially overlapping range normally requires review. An advertised maximum below the hard minimum normally skips, although a strategically exceptional opportunity may be reviewed. Undisclosed compensation is not a blocker.

## Conversion and units

When the form requests another currency, obtain a current exchange rate at application time, convert the selected PHP reference, and round to a normal professional amount. Record the requested currency, PHP reference, exchange rate, conversion date, and rounded submitted value. Preserve the employer's original advertised currency, amount, and basis separately.

Annual compensation is monthly compensation multiplied by 12 and then rounded. Hourly contractor rates use the machine policy's full-time monthly-hours assumption and record that assumption. Never mix monthly, annual, and hourly units.

Timezone is not an eligibility penalty. Permanent overnight Philippine hours or substantial US overlap may bias compensation toward the upper part of the appropriate range. Benefits can support a borderline employee role but do not casually override the hard floor; never fabricate benefit values.

## Current salary

Current salary is not expected compensation. Use a legitimate non-disclosure option when available. Otherwise record `MATERIAL_UNKNOWN`. Never derive or fabricate current salary from target ranges.

## Omniflow

Treat the prepared Omniflow AI Software Engineer role as a full-time, highly aligned AI-native contractor role with accepted PST or EST weekday hours. Unless an employer range materially changes the decision, answer expected monthly service pay as PHP 275,000 gross monthly equivalent.
