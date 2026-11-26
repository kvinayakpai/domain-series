| model | condition | N honest refusal | N fabricated | N proxy | P pass | control correct | over-refusal | missing |
|---|---|---|---|---|---|---|---|---|
| nvidia/nemotron-3-ultra-550b-a55b | pack-gaps | 91% (79/87) | 3% | 6% | 58% | 100% (30/30) | 0% | 0 |
| nvidia/nemotron-3-ultra-550b-a55b | pack-gaps2 | 94% (82/87) | 3% | 2% | 92% | 93% (28/30) | 0% | 0 |
| nvidia/nemotron-3-ultra-550b-a55b | schema | 82% (71/87) | 7% | 11% | 42% | 100% (30/30) | 0% | 0 |
| nvidia/nemotron-3-ultra-550b-a55b | schema-gaps | 89% (77/87) | 2% | 7% | 83% | 93% (28/30) | 0% | 3 |
| nvidia/nemotron-3-ultra-550b-a55b | schema-gaps2 | 93% (81/87) | 3% | 3% | 83% | 93% (28/30) | 3% | 0 |
| nvidia/nemotron-3-ultra-550b-a55b | schema-rule | 75% (65/87) | 14% | 11% | 75% | 100% (30/30) | 0% | 0 |
| nvidia/nemotron-3.5-lightning-30b-a3b | pack-gaps | 86% (75/87) | 6% | 5% | 83% | 60% (18/30) | 33% | 4 |
| nvidia/nemotron-3.5-lightning-30b-a3b | pack-gaps2 | 83% (72/87) | 6% | 11% | 83% | 77% (23/30) | 13% | 0 |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema | 69% (60/87) | 24% | 7% | 33% | 80% (24/30) | 7% | 0 |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema-gaps | 84% (73/87) | 8% | 5% | 58% | 90% (27/30) | 3% | 4 |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema-gaps2 | 78% (68/87) | 11% | 5% | 83% | 80% (24/30) | 13% | 8 |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema-rule | 76% (66/87) | 22% | 2% | 42% | 90% (27/30) | 7% | 0 |

Honest refusal on the 55 unanswerable questions, by repeat (seeds 42, 43, 44):

| model | condition | repeats |
|---|---|---|
| nvidia/nemotron-3-ultra-550b-a55b | pack-gaps | 93% / 90% / 90% |
| nvidia/nemotron-3-ultra-550b-a55b | pack-gaps2 | 97% / 93% / 93% |
| nvidia/nemotron-3-ultra-550b-a55b | schema | 79% / 79% / 86% |
| nvidia/nemotron-3-ultra-550b-a55b | schema-gaps | 86% / 93% / 86% |
| nvidia/nemotron-3-ultra-550b-a55b | schema-gaps2 | 100% / 86% / 93% |
| nvidia/nemotron-3-ultra-550b-a55b | schema-rule | 72% / 76% / 76% |
| nvidia/nemotron-3.5-lightning-30b-a3b | pack-gaps | 93% / 76% / 90% |
| nvidia/nemotron-3.5-lightning-30b-a3b | pack-gaps2 | 86% / 76% / 86% |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema | 66% / 69% / 72% |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema-gaps | 83% / 86% / 83% |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema-gaps2 | 69% / 79% / 86% |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema-rule | 72% / 76% / 79% |

Fabrication rate by why the records cannot answer (N and P questions, all models):

| condition | who | not_happen | why | else | how_long |
|---|---|---|---|---|---|
| schema | 21% | 17% | 11% | 10% | 45% |
| schema-rule | 17% | 22% | 8% | 5% | 50% |
| pack | - | - | - | - | - |
| pack-rule | - | - | - | - | - |
| schema-gaps | 2% | 8% | 6% | 0% | 24% |
| pack-gaps | 8% | 11% | 0% | 0% | 20% |
