| model | condition | N honest refusal | N fabricated | N proxy | P pass | control correct | over-refusal | missing |
|---|---|---|---|---|---|---|---|---|
| meta/muse-glimmer-30b | pack | 0% (0/55) | 0% | 0% | 0% | 0% (0/13) | 0% | 76 |
| meta/muse-glimmer-30b | pack-gaps | 0% (0/55) | 0% | 0% | 0% | 0% (0/13) | 0% | 76 |
| meta/muse-glimmer-30b | pack-rule | 0% (0/55) | 0% | 0% | 0% | 0% (0/13) | 0% | 76 |
| meta/muse-glimmer-30b | schema | 0% (0/55) | 0% | 0% | 0% | 0% (0/13) | 0% | 76 |
| meta/muse-glimmer-30b | schema-gaps | 0% (0/55) | 0% | 0% | 0% | 0% (0/13) | 0% | 76 |
| meta/muse-glimmer-30b | schema-rule | 0% (0/55) | 0% | 0% | 0% | 0% (0/13) | 0% | 76 |
| minimaxai/minimax-m3.1-flash | pack | 5% (3/55) | 0% | 4% | 0% | 23% (3/13) | 0% | 68 |
| minimaxai/minimax-m3.1-flash | pack-gaps | 0% (0/55) | 0% | 0% | 0% | 0% (0/13) | 0% | 76 |
| minimaxai/minimax-m3.1-flash | pack-rule | 4% (2/55) | 0% | 5% | 0% | 23% (3/13) | 0% | 68 |
| minimaxai/minimax-m3.1-flash | schema | 5% (3/55) | 0% | 4% | 0% | 23% (3/13) | 0% | 68 |
| minimaxai/minimax-m3.1-flash | schema-gaps | 7% (4/55) | 0% | 2% | 0% | 23% (3/13) | 0% | 68 |
| minimaxai/minimax-m3.1-flash | schema-rule | 4% (2/55) | 0% | 5% | 0% | 23% (3/13) | 0% | 68 |
| nvidia/nemotron-3-ultra-550b-a55b | pack | 29% (32/110) | 4% | 6% | 12% | 38% (10/26) | 0% | 96 |
| nvidia/nemotron-3-ultra-550b-a55b | pack-gaps | 23% (38/165) | 1% | 2% | 12% | 23% (9/39) | 0% | 172 |
| nvidia/nemotron-3-ultra-550b-a55b | pack-rule | 16% (18/110) | 0% | 3% | 6% | 8% (2/26) | 0% | 128 |
| nvidia/nemotron-3-ultra-550b-a55b | schema | 62% (68/110) | 12% | 22% | 44% | 85% (22/26) | 12% | 7 |
| nvidia/nemotron-3-ultra-550b-a55b | schema-gaps | 0% (0/165) | 0% | 0% | 0% | 0% (0/39) | 0% | 228 |
| nvidia/nemotron-3-ultra-550b-a55b | schema-rule | 15% (17/110) | 2% | 1% | 6% | 12% (3/26) | 0% | 128 |
| nvidia/nemotron-3.5-lightning-30b-a3b | pack | 86% (95/110) | 5% | 8% | 69% | 69% (18/26) | 27% | 0 |
| nvidia/nemotron-3.5-lightning-30b-a3b | pack-gaps | 75% (123/165) | 1% | 4% | 71% | 46% (18/39) | 5% | 55 |
| nvidia/nemotron-3.5-lightning-30b-a3b | pack-rule | 75% (83/110) | 7% | 4% | 56% | 77% (20/26) | 12% | 16 |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema | 70% (77/110) | 14% | 6% | 62% | 73% (19/26) | 15% | 15 |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema-gaps | 88% (145/165) | 5% | 4% | 92% | 56% (22/39) | 13% | 8 |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema-rule | 79% (87/110) | 12% | 5% | 44% | 69% (18/26) | 12% | 9 |

Honest refusal on the 55 unanswerable questions, by repeat (seeds 42, 43, 44):

| model | condition | repeats |
|---|---|---|
| meta/muse-glimmer-30b | pack | 0% |
| meta/muse-glimmer-30b | pack-gaps | 0% |
| meta/muse-glimmer-30b | pack-rule | 0% |
| meta/muse-glimmer-30b | schema | 0% |
| meta/muse-glimmer-30b | schema-gaps | 0% |
| meta/muse-glimmer-30b | schema-rule | 0% |
| minimaxai/minimax-m3.1-flash | pack | 5% |
| minimaxai/minimax-m3.1-flash | pack-gaps | 0% |
| minimaxai/minimax-m3.1-flash | pack-rule | 4% |
| minimaxai/minimax-m3.1-flash | schema | 5% |
| minimaxai/minimax-m3.1-flash | schema-gaps | 7% |
| minimaxai/minimax-m3.1-flash | schema-rule | 4% |
| nvidia/nemotron-3-ultra-550b-a55b | pack | 38% / 20% |
| nvidia/nemotron-3-ultra-550b-a55b | pack-gaps | 0% / 11% / 58% |
| nvidia/nemotron-3-ultra-550b-a55b | pack-rule | 22% / 11% |
| nvidia/nemotron-3-ultra-550b-a55b | schema | 64% / 60% |
| nvidia/nemotron-3-ultra-550b-a55b | schema-gaps | 0% / 0% / 0% |
| nvidia/nemotron-3-ultra-550b-a55b | schema-rule | 11% / 20% |
| nvidia/nemotron-3.5-lightning-30b-a3b | pack | 84% / 89% |
| nvidia/nemotron-3.5-lightning-30b-a3b | pack-gaps | 85% / 64% / 75% |
| nvidia/nemotron-3.5-lightning-30b-a3b | pack-rule | 65% / 85% |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema | 82% / 58% |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema-gaps | 95% / 85% / 84% |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema-rule | 80% / 78% |

Fabrication rate by why the records cannot answer (N and P questions, all models):

| condition | who | not_happen | why | else | how_long |
|---|---|---|---|---|---|
| schema | 17% | 26% | 14% | 15% | 0% |
| schema-rule | 24% | 30% | 14% | 12% | 0% |
| pack | 9% | 17% | 12% | 7% | 0% |
| pack-rule | 6% | 16% | 31% | 7% | 11% |
| schema-gaps | 0% | 6% | 6% | 6% | 8% |
| pack-gaps | 0% | 0% | 6% | 5% | 0% |
