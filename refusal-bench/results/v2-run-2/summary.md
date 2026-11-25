| model | condition | N honest refusal | N fabricated | N proxy | P pass | control correct | over-refusal | missing |
|---|---|---|---|---|---|---|---|---|
| minimaxai/minimax-m3.1-flash | pack | 29% (16/55) | 5% | 18% | 25% | 54% (7/13) | 0% | 36 |
| minimaxai/minimax-m3.1-flash | pack-gaps | 24% (13/55) | 2% | 7% | 12% | 31% (4/13) | 0% | 52 |
| minimaxai/minimax-m3.1-flash | pack-rule | 33% (18/55) | 4% | 7% | 12% | 38% (5/13) | 0% | 44 |
| minimaxai/minimax-m3.1-flash | schema | 15% (8/55) | 0% | 5% | 0% | 31% (4/13) | 0% | 60 |
| minimaxai/minimax-m3.1-flash | schema-gaps | 25% (14/55) | 2% | 5% | 12% | 31% (4/13) | 0% | 52 |
| minimaxai/minimax-m3.1-flash | schema-rule | 31% (17/55) | 2% | 7% | 0% | 54% (7/13) | 0% | 44 |
| nvidia/nemotron-3-ultra-550b-a55b | pack | 47% (52/110) | 11% | 11% | 25% | 77% (20/26) | 0% | 49 |
| nvidia/nemotron-3-ultra-550b-a55b | pack-gaps | 90% (148/165) | 1% | 6% | 79% | 92% (36/39) | 5% | 7 |
| nvidia/nemotron-3-ultra-550b-a55b | pack-rule | 64% (70/110) | 8% | 5% | 44% | 77% (20/26) | 0% | 36 |
| nvidia/nemotron-3-ultra-550b-a55b | schema | 60% (66/110) | 12% | 11% | 50% | 69% (18/26) | 8% | 28 |
| nvidia/nemotron-3-ultra-550b-a55b | schema-gaps | 79% (130/165) | 2% | 11% | 71% | 90% (35/39) | 0% | 20 |
| nvidia/nemotron-3-ultra-550b-a55b | schema-rule | 41% (45/110) | 9% | 15% | 31% | 65% (17/26) | 0% | 56 |
| nvidia/nemotron-3.5-lightning-30b-a3b | pack-gaps | 82% (136/165) | 1% | 3% | 88% | 54% (21/39) | 13% | 31 |
| nvidia/nemotron-3.5-lightning-30b-a3b | pack-rule | 85% (47/55) | 9% | 5% | 75% | 62% (8/13) | 23% | 0 |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema | 72% (79/110) | 8% | 7% | 38% | 69% (18/26) | 15% | 21 |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema-gaps | 93% (51/55) | 4% | 2% | 100% | 85% (11/13) | 0% | 2 |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema-rule | 67% (37/55) | 27% | 5% | 75% | 77% (10/13) | 0% | 0 |

Honest refusal on the 55 unanswerable questions, by repeat (seeds 42, 43, 44):

| model | condition | repeats |
|---|---|---|
| minimaxai/minimax-m3.1-flash | pack | 29% |
| minimaxai/minimax-m3.1-flash | pack-gaps | 24% |
| minimaxai/minimax-m3.1-flash | pack-rule | 33% |
| minimaxai/minimax-m3.1-flash | schema | 15% |
| minimaxai/minimax-m3.1-flash | schema-gaps | 25% |
| minimaxai/minimax-m3.1-flash | schema-rule | 31% |
| nvidia/nemotron-3-ultra-550b-a55b | pack | 47% / 47% |
| nvidia/nemotron-3-ultra-550b-a55b | pack-gaps | 84% / 89% / 96% |
| nvidia/nemotron-3-ultra-550b-a55b | pack-rule | 58% / 69% |
| nvidia/nemotron-3-ultra-550b-a55b | schema | 44% / 76% |
| nvidia/nemotron-3-ultra-550b-a55b | schema-gaps | 71% / 82% / 84% |
| nvidia/nemotron-3-ultra-550b-a55b | schema-rule | 42% / 40% |
| nvidia/nemotron-3.5-lightning-30b-a3b | pack-gaps | 95% / 75% / 78% |
| nvidia/nemotron-3.5-lightning-30b-a3b | pack-rule | 85% |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema | 69% / 75% |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema-gaps | 93% |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema-rule | 67% |

Fabrication rate by why the records cannot answer (N and P questions, all models):

| condition | who | not_happen | why | else | how_long |
|---|---|---|---|---|---|
| schema | 15% | 30% | 16% | 9% | 8% |
| schema-rule | 20% | 31% | 21% | 16% | 0% |
| pack | 14% | 52% | 20% | 8% | 0% |
| pack-rule | 9% | 18% | 25% | 11% | 0% |
| schema-gaps | 0% | 17% | 0% | 2% | 0% |
| pack-gaps | 0% | 8% | 3% | 1% | 0% |
