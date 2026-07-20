import type { CollectionEntry } from 'astro:content';

export type NoteEntry = CollectionEntry<'notes'>;

export function isPublishedNote(entry: NoteEntry) {
  return !entry.data.draft;
}

export function sortNotesNewestFirst(a: NoteEntry, b: NoteEntry) {
  return b.data.publishedDate.getTime() - a.data.publishedDate.getTime();
}

export function noteSlug(entry: NoteEntry) {
  return entry.id.replace(/\.(md|mdx)$/, '');
}

export function noteUrl(entry: NoteEntry) {
  return `/notes/${noteSlug(entry)}/`;
}

export function readingTime(body: string) {
  const plainText = body
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/[#>*_`|\[\]()-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
  const words = plainText ? plainText.split(' ').length : 0;
  return {
    words,
    minutes: Math.max(1, Math.ceil(words / 220)),
    label: `${Math.max(1, Math.ceil(words / 220))} min read`,
  };
}

export function formatNoteDate(date: Date) {
  return new Intl.DateTimeFormat('en', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    timeZone: 'UTC',
  }).format(date);
}
