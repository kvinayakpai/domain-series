import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const posts = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/posts' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    order: z.number(),
    slug: z.string(),
    demoAnchor: z.string(),
    hook: z.string(),
    personas: z.array(z.object({ name: z.string(), role: z.string() })),
    kpis: z.array(z.string()),
    learningPath: z.array(z.string()),
  }),
});

export const collections = { posts };
