# Analytics events

Google Analytics loads only when `PUBLIC_GA_MEASUREMENT_ID` is configured. A single delegated click handler reads `data-analytics-event` and `data-analytics-location`; it sends no email content or other personal data and does nothing when analytics is unavailable or blocked.

| Event | Trigger | Parameter | Location |
|---|---|---|---|
| `cv_download` | CV link click | `link_location` | Contact |
| `contact_email_click` | Primary email link click | `link_location` | Contact |
| `linkedin_click` | LinkedIn outbound link click | `link_location` | Contact |
| `github_click` | GitHub outbound link click | `link_location` | Contact |
| `ordr_now_click` | Ordr.now outbound link click | `link_location` | Home, Work index, Ordr.now case study |
| `article_open` | Cornerstone article link click | `link_location` | Home Latest Note, AI-Native Engineering |

Normal pageviews remain the measurement source for article views. Do not add click events to ordinary article navigation.
