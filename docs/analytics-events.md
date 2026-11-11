# Analytics events

Google Analytics loads only when `PUBLIC_GA_MEASUREMENT_ID` is configured. A single delegated click handler reads `data-analytics-event` and `data-analytics-location`; it sends no email content or other personal data and does nothing when analytics is unavailable or blocked.

| Event | Trigger | Parameter | Location |
|---|---|---|---|
| `cv_download` | CV link click | `link_location` | Contact |
| `contact_email_click` | Primary email link click | `link_location` | Contact |
| `linkedin_click` | LinkedIn outbound link click | `link_location` | Contact |
| `github_click` | GitHub outbound link click | `link_location` | Contact |
| `ordr_now_click` | Ordr.now outbound link click | `link_location` | Home, Work index, Ordr.now case study |
| `article_open` | Note link click from a non-Notes page | `link_location` | Home latest notes, Approach |

`link_location` values in use:

- Contact: `contact_primary`, `contact_links`
- Home: `home_anchor_case`, `home_latest_note`
- Work: `work_index`, `ordr_case_study`
- Approach: `ai_native_engineering_evidence`, `ai_native_engineering_practice`, `ai_native_engineering_setup`

Removed in the November 2026 reorganization: `ai_native_engineering_intro` and the Home method link.

Normal pageviews remain the measurement source for article views. Do not add click events to ordinary article navigation.
