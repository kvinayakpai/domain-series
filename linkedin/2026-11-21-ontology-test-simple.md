# LinkedIn post (draft, 21 Nov 2026): the ontology experiment, simple version

Status: draft, not yet published. For everyone, not only data people.
The site's blogs on this are posts 16 and 17 of Season 2.

---

My learning from this experiment – "A machine can draft the tables of a business. It cannot know what the numbers mean."

So far I have covered 12 KPIs in this series. This is where it is leading.

Over two days I ran an open-source tool from NVIDIA, Auto-Ontology, on one grocery store's records. It reads a database and drafts an ontology, which is the written-down meaning of the business. Then I asked it four questions about one product, 5 kg atta, in June 2026:

1) How many bags were sold?
2) How many shoppers left without a bag?
3) How often was it on the shelf?
4) What were the lost sales?

What I found –

The records can answer 1 and 3. 567 bags sold, and 6 of 8 shelf checks found it on the shelf (75%).

Nobody records 2 and 4. A shopper who walks away leaves no row in any table. The machine's draft had no term for it either.

Small AI models answered anyway, with confident numbers from the wrong table. When I wrote down what each table really means, NVIDIA's model stopped guessing and said "no record holds this". Claude's Sonnet and Opus were careful even without it. The smallest models kept guessing.

The lesson – the tables were never the problem. The missing piece is business meaning, and a person who knows the business has to write it down. More on this in the coming posts.

Curious to know what you think 🙏
