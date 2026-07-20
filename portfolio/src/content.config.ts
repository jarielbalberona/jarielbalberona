import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const work = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/work' }),
  schema: z.object({
    title: z.string(),
    summary: z.string(),
    status: z.string(),
    timeframe: z.string(),
    featured: z.boolean().default(false),
    order: z.number().default(100),
    liveUrl: z.string().url().optional(),
    role: z.string(),
    stack: z.array(z.string()),
    highlights: z.array(z.string()),
    context: z.string(),
    ownership: z.array(z.string()),
    constraints: z.array(z.string()),
    changes: z.array(z.string()),
    impact: z.string(),
  }),
});

const noteTags = z.enum([
  'agentic-engineering',
  'ai-native-engineering',
  'software-delivery',
  'verification',
  'bounded-autonomy',
  'context-engineering',
]);

const notes = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/notes' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    publishedDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    draft: z.boolean().default(true),
    tags: z.array(noteTags).min(1),
    canonical: z.string().url().optional(),
    ogImage: z.string(),
    summary: z.string(),
    featured: z.boolean().default(false),
  }),
});

export const collections = { work, notes };
