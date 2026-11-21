# LinkedIn post (draft, 21 Nov 2026): the ontology test, detailed version

Status: draft, not yet published. With all the numbers.

---

My learning from this experiment – "Writing the business down helps, but only for models strong enough to use it."

So far I have covered 12 KPIs in this series. This is where it is leading: ontology, the written-down meaning of a business, as the missing layer under every KPI.

The test – one store (Store 014), one product (5 kg atta), June 2026, four questions:
1) Bags sold  2) Shoppers who left without  3) On-shelf availability  4) Lost sales

The true answers –
1) 567 bags (till lines, matched on the pack's code)
2) and 4) No table holds them. Demand and lost sales are recorded nowhere
3) 75% – 6 of 8 shelf audits found it on the shelf. Book stock says otherwise, as it only copies other records

Step 1 – I let NVIDIA's open-source Auto-Ontology draft the ontology from the database. With NVIDIA's own model (Nemotron 3.5 Lightning) it took 10 minutes and gave 21 terms, one per table. None for demand or lost sales.

Step 2 – Without the knowledge, Nemotron got 1 and 3 right. For 2 it said 2 shoppers (really the 2 times the shelf was found empty). For 4 it said 3 bags (really the write-offs). With the knowledge added (table meanings, joins and 12 rules), it said no record holds those two.

Step 3 – I gave the same test to fresh Claude agents, with and without the knowledge:
- All six got 1 and 3 right
- Sonnet and Opus said "no record" for 2, even without the knowledge
- Haiku turned forecasts into 43 to 84 shoppers, with and without the knowledge
- For 4, the models gave guesses from 43 to 170 bags. All were labelled as estimates, none was a record
- A 7B open model I tested earlier was still wrong after the knowledge

Two cautions – one run per model, and this tests Claude answering the questions, not Auto-Ontology's own agent. Read it as a sign, not proof.

The lesson – a machine can draft the tables. The meaning has to come from people who know the business, and the model has to be strong enough to respect it. That is where the KPI series is heading.

Curious to know what you think 🙏
