# jarielbalberona.dev

This directory is the canonical public site app for `jarielbalberona.dev`.

The site presents Jariel Balberona as a Staff-Level AI-Native Software Engineer with evidence grounded in production product, platform, architecture, and delivery work.

## Source-of-truth stack

- Astro
- TypeScript
- Tailwind CSS v4
- Astro content collections for Work
- Render Static Site deployment

## Content authority

- `src/data/site.ts`: site URL, identity, navigation, and global metadata defaults
- `src/data/cv.json`: employment chronology, CV roles, and selected experience facts
- `src/content/work/`: public Work case studies
- Astro page files: Home, AI-Native Engineering, Now, and Contact

Unused parallel Markdown page copies were removed so public copy does not drift between two sources.

## CV generation

`npm run build:cv` regenerates `public/jariel-balberona-cv.pdf` from `src/data/cv.json` in an isolated `uv` environment. Do not patch the PDF independently of the structured source.

## Render deployment

Render deploys the app as a static site using the repository-level `render.yaml`.

- Root directory: `portfolio`
- Build command: `npm ci && npm run build`
- Publish directory: `dist`
- Redirects: managed in `../render.yaml`

No server adapter is required.

## Analytics

Google Analytics is optional and disabled unless `PUBLIC_GA_MEASUREMENT_ID` is set in Render.

## Working rules

- Do not add a CMS, database, blog, or client-heavy runtime without a concrete need.
- Do not publish confidential client identities, repositories, domains, scripts, prompts, environments, screenshots, customer data, or internal operating details.
- Keep public claims specific, attributable, and defensible.
