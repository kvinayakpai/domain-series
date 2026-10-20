import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';

export async function GET(context) {
  const base = import.meta.env.BASE_URL;
  const posts = (await getCollection('posts'))
    .filter((p) => !p.data.draft)
    .sort((a, b) => b.data.pubDate - a.data.pubDate);
  return rss({
    title: 'Why Domain Matters',
    description: 'Real operational failures in Indian grocery retail, logistics and payments, seen through the people involved, with demos you can run.',
    site: new URL(base, context.site).toString(),
    items: posts.map((p) => ({
      title: p.data.title,
      description: p.data.description,
      pubDate: p.data.pubDate,
      link: `${base}${p.data.slug}/`,
    })),
    customData: '<language>en-in</language>',
  });
}
