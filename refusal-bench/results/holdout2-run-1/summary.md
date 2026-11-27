| model | condition | N honest refusal | N fabricated | N proxy | P pass | control correct | over-refusal | missing |
|---|---|---|---|---|---|---|---|---|
| nvidia/nemotron-3-ultra-550b-a55b | pack-gaps2 | 87% (73/84) | 5% | 8% | 50% | 96% (23/24) | 0% | 0 |
| nvidia/nemotron-3-ultra-550b-a55b | schema | 67% (56/84) | 24% | 10% | 25% | 96% (23/24) | 0% | 0 |
| nvidia/nemotron-3-ultra-550b-a55b | schema-gaps | 89% (75/84) | 8% | 2% | 33% | 96% (23/24) | 4% | 0 |
| nvidia/nemotron-3-ultra-550b-a55b | schema-gaps2 | 87% (73/84) | 6% | 7% | 75% | 92% (22/24) | 0% | 0 |
| nvidia/nemotron-3.5-lightning-30b-a3b | pack-gaps2 | 88% (74/84) | 7% | 2% | 75% | 67% (16/24) | 33% | 3 |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema | 70% (59/84) | 30% | 0% | 33% | 92% (22/24) | 4% | 0 |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema-gaps | 85% (71/84) | 11% | 1% | 75% | 83% (20/24) | 8% | 4 |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema-gaps2 | 87% (73/84) | 7% | 2% | 58% | 62% (15/24) | 21% | 4 |

Honest refusal on the 55 unanswerable questions, by repeat (seeds 42, 43, 44):

| model | condition | repeats |
|---|---|---|
| nvidia/nemotron-3-ultra-550b-a55b | pack-gaps2 | 93% / 86% / 82% |
| nvidia/nemotron-3-ultra-550b-a55b | schema | 71% / 61% / 68% |
| nvidia/nemotron-3-ultra-550b-a55b | schema-gaps | 89% / 89% / 89% |
| nvidia/nemotron-3-ultra-550b-a55b | schema-gaps2 | 82% / 93% / 86% |
| nvidia/nemotron-3.5-lightning-30b-a3b | pack-gaps2 | 86% / 93% / 86% |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema | 75% / 68% / 68% |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema-gaps | 79% / 86% / 89% |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema-gaps2 | 79% / 89% / 93% |

Fabrication rate by why the records cannot answer (N and P questions, all models):

| condition | who | not_happen | why | else | how_long |
|---|---|---|---|---|---|
| schema | 30% | 26% | 25% | 20% | 50% |
| schema-rule | - | - | - | - | - |
| pack | - | - | - | - | - |
| pack-rule | - | - | - | - | - |
| schema-gaps | 10% | 9% | 0% | 7% | 32% |
| pack-gaps | - | - | - | - | - |
