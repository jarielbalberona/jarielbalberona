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

export const collections = { work };
