# LinkedIn post (draft, 21 Nov 2026): the ontology experiment, detailed version

Status: draft, not yet published. With all the details.
The site's blogs on this are posts 16 and 17 of Season 2.

---

My learning from this experiment – "A machine can draft the tables. The meaning has to come from people, and the model has to be strong enough to respect it."

So far I have covered 18 KPIs in this series. This is where it is leading: ontology, the written-down meaning of a business, under every KPI.

The test – Store 014, 5 kg atta, June 2026, four questions: bags sold, shoppers who left without, on-shelf availability, lost sales.

The true answers –
1) 567 bags (till lines, matched on the pack's code)
2) and 4) No table holds them. Demand and lost sales are recorded nowhere
3) 75% – 6 of 8 shelf audits found it on the shelf. Book stock disagrees, as it only copies other records

Day 1 – NVIDIA's open-source Auto-Ontology on small open models, on GitHub's machines:
- The draft took 44 minutes and gave 90 terms. None for demand or lost sales
- A 7B model answered confidently and wrongly: 660 bags sold (the goods receipts) and availability from the wrong table
- With my 12 rules and table meanings added, it still said 567 shoppers left without and 24 "lost sales" (the days with sales)
- Its coverage check passed every question, every time

Day 2 – NVIDIA's own model (Nemotron 3.5 Lightning), a 10-minute draft of 21 terms:
- Without the knowledge: 567 and 75% right. It said 2 shoppers (the 2 empty shelf audits) and 3 lost bags (the write-offs)
- With the knowledge: it said no record holds those two

Then I gave the same test to six fresh Claude agents, with and without the knowledge:
- All six got 567 and 75% right
- Sonnet and Opus said "no record" for shoppers even without the knowledge
- Haiku turned forecasts into 43 to 84 shoppers, with and without
- For lost sales the guesses ranged from 43 to 170 bags, all labelled estimates

Cautions – one run per model, and the Claude test checks Claude, not Auto-Ontology's own agent. A sign, not proof.

The lesson – the tool drafted names for tables, never the meaning. Written-down knowledge turned NVIDIA's guesses into honest answers. Sonnet and Opus were careful without it, and Haiku and the 7B model guessed anyway. That is where the KPI series is heading.

Curious to know what you think 🙏
