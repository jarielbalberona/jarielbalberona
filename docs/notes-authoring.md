# Notes authoring

Notes live in `portfolio/src/content/notes/` as Markdown. The filename becomes the route slug: `example.md` becomes `/notes/example` when published.

## Frontmatter

The typed schema in `portfolio/src/content.config.ts` requires:

- `title`: public article title
- `description`: metadata description
- `publishedDate`: publication date in `YYYY-MM-DD` form
- `draft`: `true` or `false`
- `tags`: one or more values from the controlled taxonomy
- `ogImage`: root-relative public image path
- `summary`: concise Notes-index summary

Optional fields are `updatedDate`, an absolute `canonical` URL, and `featured`. Only use `updatedDate` after a substantive published revision. Do not change `publishedDate` to simulate freshness.

Allowed tags are `agentic-engineering`, `ai-native-engineering`, `software-delivery`, `verification`, `bounded-autonomy`, and `context-engineering`. Extend the taxonomy only when several articles need a genuinely new subject.

## Draft and discovery behavior

Set `draft: true` throughout review. Drafts do not generate routes and are excluded from the Notes index, related links, RSS, and the generated sitemap. Switching to `draft: false` is the publication action.

Use a 1200 × 630 PNG or JPEG for article-specific social previews. Keep the title readable, use the restrained site identity, optimize file size, and confirm the absolute production asset URL returns 200.

## Publication checklist

1. Confirm every public claim is independently demonstrable, conservatively personally attestable, generalized, or clearly labeled as opinion.
2. Scan for confidential identities, private domains, internal identifiers, scripts, prompts, operating procedures, and unsupported metrics.
3. Check heading hierarchy, generated table-of-contents anchors, links, tables, code overflow, and image alternative text.
4. Set final title, description, summary, dates, tags, canonical override if needed, and Open Graph image.
5. Run `npm run check` and `npm run build` from `portfolio/`.
6. Preview with `npm run preview` and inspect desktop and mobile article layouts, metadata, JSON-LD, RSS, and sitemap.
7. Set `draft: false`, rebuild, and confirm the route appears once in the Notes index, RSS, and sitemap.
8. After deployment, verify the article, image, canonical URL, metadata, structured data, and external discovery submissions.

RSS is generated at `/rss.xml`; the Astro sitemap integration discovers only pages emitted by the production build. No manual feed or sitemap entry is required.
