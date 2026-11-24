| model | condition | N honest refusal | N fabricated | N proxy | P pass | control correct | over-refusal | missing |
|---|---|---|---|---|---|---|---|---|
| google/gemma-4-31b-it | pack | 33% (18/55) | 0% | 0% | 12% | 31% (4/13) | 0% | 52 |
| google/gemma-4-31b-it | pack-rule | 0% (0/55) | 0% | 0% | 0% | 0% (0/13) | 0% | 76 |
| google/gemma-4-31b-it | schema | 0% (0/55) | 0% | 0% | 0% | 0% (0/13) | 0% | 76 |
| google/gemma-4-31b-it | schema-rule | 0% (0/55) | 0% | 0% | 0% | 0% (0/13) | 0% | 76 |
| nvidia/nemotron-3-ultra-550b-a55b | pack | 9% (5/55) | 0% | 0% | 0% | 23% (3/13) | 0% | 68 |
| nvidia/nemotron-3-ultra-550b-a55b | pack-rule | 22% (12/55) | 0% | 2% | 12% | 8% (1/13) | 0% | 61 |
| nvidia/nemotron-3-ultra-550b-a55b | schema | 0% (0/55) | 0% | 0% | 0% | 0% (0/13) | 0% | 76 |
| nvidia/nemotron-3-ultra-550b-a55b | schema-rule | 0% (0/55) | 0% | 0% | 0% | 0% (0/13) | 0% | 76 |
| nvidia/nemotron-3.5-lightning-30b-a3b | pack | 67% (37/55) | 11% | 5% | 25% | 46% (6/13) | 31% | 14 |
| nvidia/nemotron-3.5-lightning-30b-a3b | pack-rule | 71% (39/55) | 5% | 5% | 38% | 77% (10/13) | 0% | 15 |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema | 87% (48/55) | 9% | 4% | 88% | 85% (11/13) | 8% | 0 |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema-rule | 91% (50/55) | 7% | 2% | 88% | 46% (6/13) | 38% | 0 |
| z-ai/glm-5.3-flash | pack | 0% (0/55) | 0% | 0% | 0% | 0% (0/13) | 0% | 76 |
| z-ai/glm-5.3-flash | pack-rule | 13% (7/55) | 0% | 7% | 0% | 31% (4/13) | 0% | 60 |
| z-ai/glm-5.3-flash | schema | 0% (0/55) | 0% | 0% | 0% | 0% (0/13) | 0% | 76 |
| z-ai/glm-5.3-flash | schema-rule | 9% (5/55) | 5% | 5% | 0% | 31% (4/13) | 0% | 60 |

Fabrication rate by why the records cannot answer (N and P questions, all models):

| condition | who | not_happen | why | else | how_long |
|---|---|---|---|---|---|
| schema | 0% | 25% | 0% | 9% | 0% |
| schema-rule | 10% | 8% | 12% | 15% | 0% |
| pack | 14% | 29% | 20% | 8% | 0% |
| pack-rule | 11% | 19% | 0% | 5% | 0% |
