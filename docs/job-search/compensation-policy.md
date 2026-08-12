# Compensation policy

Machine-readable thresholds live in `job_search/policy/compensation_policy.json`. This document defines how to use them. The default basis is PHP gross monthly compensation.

## Employee thresholds

```yaml
hard_minimum_monthly_php: 160000
preferred_minimum_monthly_php: 180000
target_range_monthly_php:
  min: 200000
  max: 250000
default_strong_senior_monthly_php: 220000
default_ai_native_senior_monthly_php: 240000
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
default_strong_senior_monthly_php: 240000
default_ai_native_senior_monthly_php: 250000
```

- Below PHP 200,000: normally `SKIP / COMPENSATION_BELOW_MINIMUM`.
- PHP 200,000-219,999: `REVIEW / COMPENSATION_REVIEW`.
- PHP 220,000-300,000: `COMPENSATION_TARGET_MATCH`.
- Above PHP 300,000: positive.

Do not penalize an otherwise suitable full-time role merely because it uses a legitimate non-employee structure.

The maximum of either target range is not a rejection ceiling.

## High alignment and market context

For AI-native product engineering, agentic AI, coding agents, AI platforms, developer tooling or productivity, Staff-level hands-on engineering, or broad product/platform architecture ownership:

```yaml
preferred_minimum_monthly_php: 230000
stretch_target_monthly_php: 300000
```

Optimize for strong compensation without unnecessarily pricing Jariel out before an interview. High fit alone does not prove a premium budget. A Staff or exceptional agentic AI role normally supports PHP 250,000-275,000 monthly. Use PHP 275,000-300,000 or more only when the advertised range, direct international-rate evidence, Staff or Principal scope, specialized requirements, substantial architectural ownership, or recruiter budget evidence supports the higher anchor.

An overseas headquarters does not itself prove international-rate compensation. When an international employer explicitly targets Philippines-based candidates, treat localized compensation as plausible unless contrary evidence exists. A strong Senior AI-native contractor role in that market context defaults to PHP 250,000 monthly.

## Expected-compensation answers

Expected compensation is a canonical policy decision, not an unresolved applicant fact. Select it autonomously from engagement type, seniority, technical and career fit, AI alignment, ownership, advertised range, benefits, contract risk, working hours, and overall application strength.

Default single-value anchors when no better employer evidence exists:

- Standard Senior employee: PHP 220,000 monthly.
- Strong Senior AI-native employee: PHP 230,000-250,000 monthly; default PHP 240,000.
- Standard strong contractor: PHP 230,000-240,000 monthly; default PHP 240,000.
- Strong Senior AI-native contractor: default PHP 250,000 monthly.
- Staff or exceptional agentic AI role without high-budget evidence: PHP 250,000-275,000 monthly.
- Staff role with direct international-rate or other high-budget evidence: PHP 275,000-300,000 or more when supported.

Do not mechanically choose the minimum, maximum, or widest range. If the employer publishes a range that fully meets policy, use the range rather than blindly applying a default and position a strong candidate around its midpoint or higher only when scope and budget evidence justify it. Typical examples are PHP 250,000 for a PHP 200,000-300,000 range, PHP 250,000 for a PHP 220,000-260,000 range, and PHP 300,000 for a PHP 250,000-350,000 range. A partially overlapping range normally requires review. An advertised maximum below the hard minimum normally skips, although a strategically exceptional opportunity may be reviewed. Undisclosed compensation is not a blocker; use the job-specific default if the application asks for an expectation.

The submitted expectation is an initial negotiation anchor, not necessarily final accepted compensation. Preserve room for negotiation after employer interest rather than automatically maximizing the application-form answer.

## Conversion and units

When the form requests another currency, obtain a current exchange rate at application time, convert the selected PHP reference, and round to a normal professional amount. Record the requested currency, PHP reference, exchange rate, conversion date, and rounded submitted value. Preserve the employer's original advertised currency, amount, and basis separately.

Annual compensation is monthly compensation multiplied by 12 and then rounded. Hourly contractor rates use the machine policy's full-time monthly-hours assumption and record that assumption. Never mix monthly, annual, and hourly units.

Timezone is not an eligibility penalty. Permanent overnight Philippine hours or substantial US overlap may bias compensation toward the upper part of the appropriate range. Benefits can support a borderline employee role but do not casually override the hard floor; never fabricate benefit values.

## Current salary

Current salary is not expected compensation. Canonical application status is not currently employed, so answer `Not currently applicable / not currently employed`; use numeric `0` only for a strictly numeric required current-salary field. Previous or most-recent salary is separately canonicalized as PHP 200,000 monthly. Never derive either value from target ranges.

## Omniflow

Treat the prepared Omniflow AI Software Engineer role as a full-time, highly aligned AI-native contractor role with accepted PST or EST weekday hours, explicit Philippines targeting, and no advertised range proving a PHP 275,000 or higher budget. Unless the employer supplies materially different compensation evidence, answer expected monthly service pay as PHP 250,000 gross monthly equivalent with `BEST_SUPPORTED_ANSWER` provenance.
