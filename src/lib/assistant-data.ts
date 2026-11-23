// The three domains' assistant blocks, each typed against AssistantData. If one analysis script drifts
// from the shape the figures and demos read, this file stops type-checking, instead of an
// `as unknown as` cast hiding it. Server-side only (figures, KPI maths); the demos import their own JSON.
import retailAi from '../data/retail-ai.json';
import logisticsAi from '../data/logistics-ai.json';
import paymentsAi from '../data/payments-ai.json';
import type { AssistantData, AssistantDomain } from './assistant-view';

export const ASSISTANTS: Record<AssistantDomain, AssistantData> = {
  retail: retailAi.assistant,
  logistics: logisticsAi.assistant,
  payments: paymentsAi.assistant,
};
