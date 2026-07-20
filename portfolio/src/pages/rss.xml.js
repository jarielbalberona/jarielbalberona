import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import { isPublishedNote, noteUrl, sortNotesNewestFirst } from '../lib/notes';
import { siteMeta } from '../data/site';

export async function GET(context) {
  const notes = (await getCollection('notes')).filter(isPublishedNote).sort(sortNotesNewestFirst);

  return rss({
    title: 'Jariel Balberona Notes',
    description: 'Technical notes on agentic engineering, verification, bounded autonomy, and production software delivery.',
    site: context.site ?? siteMeta.url,
    items: notes.map((entry) => ({
      title: entry.data.title,
      description: entry.data.description,
      pubDate: entry.data.publishedDate,
      link: noteUrl(entry),
      categories: entry.data.tags,
    })),
    customData: '<language>en</language>',
  });
}
