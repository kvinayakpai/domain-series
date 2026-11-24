| model | condition | N honest refusal | N fabricated | N proxy | P pass | control correct | over-refusal | missing |
|---|---|---|---|---|---|---|---|---|
| google/gemma-4-31b-it | pack | 31% (17/55) | 2% | 0% | 12% | 23% (3/13) | 0% | 52 |
| google/gemma-4-31b-it | pack-rule | 0% (0/55) | 0% | 0% | 0% | 0% (0/13) | 0% | 76 |
| google/gemma-4-31b-it | schema | 5% (3/55) | 4% | 0% | 0% | 23% (3/13) | 0% | 68 |
| google/gemma-4-31b-it | schema-rule | 20% (11/55) | 2% | 0% | 12% | 15% (2/13) | 0% | 60 |
| nvidia/nemotron-3-ultra-550b-a55b | pack | 76% (42/55) | 5% | 18% | 62% | 100% (13/13) | 0% | 0 |
| nvidia/nemotron-3-ultra-550b-a55b | pack-rule | 78% (43/55) | 7% | 15% | 62% | 100% (13/13) | 0% | 0 |
| nvidia/nemotron-3-ultra-550b-a55b | schema | 71% (39/55) | 9% | 20% | 50% | 92% (12/13) | 0% | 0 |
| nvidia/nemotron-3-ultra-550b-a55b | schema-rule | 69% (38/55) | 13% | 18% | 50% | 100% (13/13) | 0% | 0 |
| nvidia/nemotron-3.5-lightning-30b-a3b | pack | 82% (45/55) | 9% | 9% | 88% | 92% (12/13) | 0% | 0 |
| nvidia/nemotron-3.5-lightning-30b-a3b | pack-rule | 91% (50/55) | 7% | 2% | 62% | 69% (9/13) | 8% | 0 |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema | 76% (42/55) | 9% | 5% | 62% | 62% (8/13) | 23% | 7 |
| nvidia/nemotron-3.5-lightning-30b-a3b | schema-rule | 85% (47/55) | 15% | 0% | 62% | 77% (10/13) | 15% | 0 |
| z-ai/glm-5.3-flash | pack | 4% (2/55) | 2% | 4% | 0% | 23% (3/13) | 0% | 68 |
| z-ai/glm-5.3-flash | pack-rule | 0% (0/55) | 0% | 0% | 0% | 0% (0/13) | 0% | 76 |
| z-ai/glm-5.3-flash | schema | 4% (2/55) | 2% | 4% | 0% | 23% (3/13) | 0% | 68 |
| z-ai/glm-5.3-flash | schema-rule | 0% (0/55) | 0% | 0% | 0% | 0% (0/13) | 0% | 76 |

Fabrication rate by why the records cannot answer (N and P questions, all models):

| condition | who | not_happen | why | else | how_long |
|---|---|---|---|---|---|
| schema | 6% | 35% | 18% | 10% | 0% |
| schema-rule | 17% | 32% | 25% | 12% | 0% |
| pack | 0% | 19% | 25% | 7% | 12% |
| pack-rule | 6% | 25% | 25% | 6% | 0% |
