| model | condition | N honest refusal | N fabricated | N proxy | P pass | control correct | over-refusal | missing |
|---|---|---|---|---|---|---|---|---|
| minimaxai/minimax-m3.1-flash | pack | 40% (22/55) | 5% | 27% | 38% | 77% (10/13) | 0% | 21 |
| minimaxai/minimax-m3.1-flash | pack-gaps | 24% (13/55) | 2% | 7% | 12% | 31% (4/13) | 0% | 52 |
| minimaxai/minimax-m3.1-flash | pack-rule | 58% (32/55) | 4% | 11% | 38% | 77% (10/13) | 0% | 21 |
| minimaxai/minimax-m3.1-flash | schema | 5% (3/55) | 0% | 4% | 0% | 23% (3/13) | 0% | 68 |
| minimaxai/minimax-m3.1-flash | schema-gaps | 25% (14/55) | 2% | 5% | 12% | 31% (4/13) | 0% | 52 |
| minimaxai/minimax-m3.1-flash | schema-rule | 29% (16/55) | 4% | 11% | 12% | 38% (5/13) | 0% | 44 |
| nvidia/nemotron-3-ultra-550b-a55b | pack | 72% (79/110) | 13% | 15% | 44% | 100% (26/26) | 0% | 0 |
| nvidia/nemotron-3-ultra-550b-a55b | pack-gaps | 91% (50/55) | 2% | 7% | 88% | 100% (13/13) | 0% | 0 |
| nvidia/nemotron-3-ultra-550b-a55b | pack-rule | 79% (87/110) | 11% | 10% | 50% | 100% (26/26) | 0% | 0 |
| nvidia/nemotron-3-ultra-550b-a55b | schema-gaps | 84% (46/55) | 4% | 13% | 88% | 100% (13/13) | 0% | 0 |
| nvidia/nemotron-3-ultra-550b-a55b | schema-rule | 68% (75/110) | 11% | 21% | 62% | 96% (25/26) | 0% | 0 |

Honest refusal on the 55 unanswerable questions, by repeat (seeds 42, 43, 44):

| model | condition | repeats |
|---|---|---|
| minimaxai/minimax-m3.1-flash | pack | 40% |
| minimaxai/minimax-m3.1-flash | pack-gaps | 24% |
| minimaxai/minimax-m3.1-flash | pack-rule | 58% |
| minimaxai/minimax-m3.1-flash | schema | 5% |
| minimaxai/minimax-m3.1-flash | schema-gaps | 25% |
| minimaxai/minimax-m3.1-flash | schema-rule | 29% |
| nvidia/nemotron-3-ultra-550b-a55b | pack | 71% / 73% |
| nvidia/nemotron-3-ultra-550b-a55b | pack-gaps | 91% |
| nvidia/nemotron-3-ultra-550b-a55b | pack-rule | 80% / 78% |
| nvidia/nemotron-3-ultra-550b-a55b | schema-gaps | 84% |
| nvidia/nemotron-3-ultra-550b-a55b | schema-rule | 69% / 67% |

Fabrication rate by why the records cannot answer (N and P questions, all models):

| condition | who | not_happen | why | else | how_long |
|---|---|---|---|---|---|
| schema | 0% | - | - | 0% | - |
| schema-rule | 16% | 30% | 21% | 9% | 0% |
| pack | 25% | 42% | 33% | 5% | 0% |
| pack-rule | 25% | 26% | 20% | 8% | 0% |
| schema-gaps | 0% | 33% | 0% | 0% | 0% |
| pack-gaps | 0% | 20% | 0% | 2% | 0% |
