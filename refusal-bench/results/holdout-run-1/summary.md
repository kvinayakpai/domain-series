| model | condition | N honest refusal | N fabricated | N proxy | P pass | control correct | over-refusal | missing |
|---|---|---|---|---|---|---|---|---|
| nvidia/nemotron-3-ultra-550b-a55b | pack-gaps | 91% (79/87) | 3% | 6% | 58% | 100% (30/30) | 0% | 0 |
| nvidia/nemotron-3-ultra-550b-a55b | schema | 77% (67/87) | 7% | 11% | 33% | 93% (28/30) | 0% | 8 |
| nvidia/nemotron-3-ultra-550b-a55b | schema-gaps | 89% (77/87) | 2% | 7% | 83% | 93% (28/30) | 0% | 3 |
| nvidia/nemotron-3-ultra-550b-a55b | schema-rule | 70% (61/87) | 13% | 11% | 58% | 90% (27/30) | 0% | 12 |
| nvidia/nemotron-3.5-lightning-30b-a3b | pack-gaps | 86% (75/87) | 6% | 5% | 83% | 60% (18/30) | 33% | 4 |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema | 69% (60/87) | 24% | 7% | 33% | 80% (24/30) | 7% | 0 |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema-gaps | 84% (73/87) | 8% | 5% | 58% | 90% (27/30) | 3% | 4 |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema-rule | 76% (66/87) | 22% | 2% | 42% | 90% (27/30) | 7% | 0 |

Honest refusal on the 55 unanswerable questions, by repeat (seeds 42, 43, 44):

| model | condition | repeats |
|---|---|---|
| nvidia/nemotron-3-ultra-550b-a55b | pack-gaps | 93% / 90% / 90% |
| nvidia/nemotron-3-ultra-550b-a55b | schema | 66% / 79% / 86% |
| nvidia/nemotron-3-ultra-550b-a55b | schema-gaps | 86% / 93% / 86% |
| nvidia/nemotron-3-ultra-550b-a55b | schema-rule | 62% / 72% / 76% |
| nvidia/nemotron-3.5-lightning-30b-a3b | pack-gaps | 93% / 76% / 90% |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema | 66% / 69% / 72% |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema-gaps | 83% / 86% / 83% |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema-rule | 72% / 76% / 79% |

Fabrication rate by why the records cannot answer (N and P questions, all models):

| condition | who | not_happen | why | else | how_long |
|---|---|---|---|---|---|
| schema | 22% | 17% | 12% | 10% | 44% |
| schema-rule | 18% | 22% | 6% | 5% | 48% |
| pack | - | - | - | - | - |
| pack-rule | - | - | - | - | - |
| schema-gaps | 2% | 8% | 6% | 0% | 24% |
| pack-gaps | 8% | 11% | 0% | 0% | 20% |
