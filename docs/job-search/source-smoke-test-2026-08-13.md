# Expanded source registry smoke test — 2026-08-13

This was a discovery-only check from the Philippines. No application was prepared or submitted. Counts are a point-in-time measure of visible, title-plausible inventory, not a fit score or a promise that the role accepts applicants in the Philippines.

| Source | Reachable/current | Query checked | Plausible results observed | Geography behavior | Account/profile | Duplicate or quality notes |
| --- | --- | --- | ---: | --- | --- | --- |
| Wellfound | Yes | Senior AI Engineer; remote | 7 sampled title matches; 2 explicitly `Everywhere` | Per-listing hiring countries clearly distinguish `Everywhere` from US-only | Browse public; account/profile for hosted apply | Strong inventory, but most sampled roles were US-only or older than the preferred freshness window |
| Arc.dev | Yes | Remote software engineering / AI | 3 current visible target-role samples; board reports 3,100+ engineering listings | Location and timezone are visible per listing; sampled roles were mostly US-only | Public browse; profile/account for network or fast apply | Includes syndicated We Work Remotely inventory, so destination dedup is mandatory |
| Dynamite Jobs | Yes | Software engineering; full-stack | 15+ current target-role listings visible across skill pages | Listing-level location; one visible Remote (PH) result | Public browse; account may be used for hosted apply | Several jobs also originate at employer ATS pages |
| We Work Remotely | Yes; RSS current | Full-Stack Programming RSS | 118 feed items; manual sample found 2 directly relevant AI/backend roles | RSS exposes regions such as `Asia Only` and `Anywhere in the World` | No account for feed; destination controls apply | Toptal roles are syndicated and overlap the Toptal network source; one employer/title pair was repeated |
| Remote OK | Yes; public API current | Senior/staff/software/full-stack/AI title filter | 8 target-title matches in current API sample | Current matching sample had 0 explicit Philippines/APAC/worldwide location labels | No account for API; destination controls apply | Feed quality is mixed; resolve employer and destination before assessment |
| Remotive | Yes; free API current | Software/AI senior title filter | 6 target-title matches from 17 API results; 2 labelled APAC/worldwide | API exposes required location | No account for free feed; richer web inventory is partly gated | A.Team roles are syndicated; do not buy access to expand the feed |
| Working Nomads | Yes | Senior Software Engineer; AI | 4 relevant official listing pages sampled | `Anywhere`, APAC, country, and senior filters exist; samples were mostly US-only | Public browse; destination controls apply | Curated aggregator; expect employer-direct duplicates |
| HireTalent.ph | Yes | Software Development / senior prompt engineering | 1 relevant but stale result sampled | Source targets Philippine talent working with remote employers | Talent registration and listing unlock required for contact details | No unlock or purchase attempted; do not count locked inventory as application-ready |
| FilipinoContractors.com | Yes | Developer / software / AI | 2 engineering listings surfaced | Built for Filipino contractors; employer/client still requires verification | Public listing text; account required for salary/application functions | Salary is hidden when signed out; some surfaced roles were closed or outside target direction |
| Foundit Philippines | Yes | Senior software engineer | 0 reliably extractable target results in this check | Philippines search route works; remote/international filters must be applied in live UI | Account likely required to apply | Dynamic result page prevented a trustworthy count; retain at P2 and re-check interactively |
| RemoteTalent.ph | No | Homepage and engineering discovery | 0 | Not testable | Not testable | HTTPS connection failed; retain at P2 for later re-verification |
| Remotify.ph | Yes | Public jobs/careers search | 0 public candidate listings found | EOR information is Philippines-specific; underlying client must be resolved | No candidate job profile observed | Treat as an EOR/intermediary lead source, not a productive job board |
| Turing | Yes | Senior Software Engineer; Senior AI/ML Engineer | 2 relevant role-family landing flows verified | Global network with explicit US-overlap requirements | Profile, tests, and interviews required | Talent-network onboarding, not ordinary per-job submission; official FAQ says developer signup is free |
| Toptal | Yes through normal web route; direct curl challenged | Developer talent application | 1 developer-network entry flow; per-job inventory unavailable before acceptance | Global network | Account plus 3–8 week vetting process | Do not model network vetting as an individual job application |
| Contra | Yes | Remote software engineer opportunities | 9 relevant projects visible on the featured page | Remote scope shown per engagement; client/location verification remains necessary | Account/profile required to apply | Mixes substantial ongoing work with low-value fixed-price projects; compensation floor is essential |
| JustRemote | Yes | Remote developer jobs | 8 relevant titles among 15 visible developer listings | Applicant-location index works but did not include Philippines | Public browse; destination controls apply | Exact duplicates observed for Speechify and AssemblyAI listings; P3 incremental value only |
| Upwork | Public listings indexable; direct curl challenged | Senior full-stack / agentic AI | 4 relevant listings sampled; at least 3 labelled worldwide | Per-listing worldwide and timezone terms available | Existing account required; proposals ordinarily use Connects | No Connects spent, no boost used, and no proposal prepared |

## Duplicate findings

- Arc syndicates We Work Remotely inventory.
- We Work Remotely currently carries Toptal-branded opportunities, overlapping the Toptal network route.
- JustRemote displayed exact repeated employer/title listings for Speechify and AssemblyAI.
- Remotive carried A.Team talent-network roles also discoverable through other remote aggregators.
- Aggregator discoveries must retain their original source row while canonicalizing to a resolved employer-direct or ATS destination URL.

## Result

The sources are suitable for a tiered recurring rotation, with three caveats: RemoteTalent.ph is presently unreachable, Remotify.ph did not expose a public job inventory, and HireTalent.ph hides consequential contact/application details behind registration/unlock. None of those caveats permits paid access or relaxed job-quality gates.
