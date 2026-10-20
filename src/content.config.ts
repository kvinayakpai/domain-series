import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const posts = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/posts' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    order: z.number(),
    slug: z.string(),
    demoAnchor: z.string(),
    /** What the system records. Shown in the record voice. */
    record: z.string(),
    /** What actually happened. */
    reality: z.string(),
    author: z.string().default('Vinayak'),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    draft: z.boolean().default(false),
    /** Path under public/ for the link-preview image. */
    image: z.string(),
    // Outline fields, used only while a post is a draft.
    personas: z.array(z.object({ name: z.string(), role: z.string() })).optional(),
    kpis: z.array(z.string()).optional(),
    learningPath: z.array(z.string()).optional(),
  }),
});

/** Technical companions: the practitioner's version of a post, at /<post>/technical/. */
const companions = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/companions' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    /** The slug of the post this companion belongs to. */
    post: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    /** Path under public/ for the notebook, e.g. 'notebooks/retail.ipynb'. */
    notebook: z.string().optional(),
    image: z.string().optional(),
  }),
});

export const collections = { posts, companions };
