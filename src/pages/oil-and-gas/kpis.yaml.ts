// The Oil & Gas season's KPIs as YAML, in reading order: the same text the posts use. The pictures
// (scripts/images/oil-gas-cards.mjs) read this file from the build, so a card cannot drift from its post.
import { OG_KPIS, ogKpiNumber } from '../../lib/oil-gas';

// JSON strings are valid YAML double-quoted scalars.
const q = (s: string) => JSON.stringify(s);

export function GET() {
  const lines = [
    '# Oil & Gas KPIs, x-rayed: https://kvinayakpai.github.io/domain-series/oil-and-gas/',
    '# Each KPI: what it drives, how it is usually computed, what that record cannot see, the check',
    '# that exposes the gap, the rule to give an AI agent, and Field 014\'s or Refinery 014\'s two numbers.',
    '# KPIs whose posts are not out yet carry only their number, name and part.',
    'kpis:',
  ];
  for (const k of OG_KPIS) {
    lines.push(`  - id: ${k.id}`, `    n: ${ogKpiNumber(k.id)}`, `    name: ${q(k.name)}`, `    part: ${k.part}`);
    if (k.agent) {
      lines.push(
        `    drives: ${q(k.drives ?? '')}`,
        `    usually_computed_from: ${q(k.computed ?? '')}`,
        `    blind_spot: ${q(k.blind ?? '')}`,
        `    domain_check: ${q(k.check ?? '')}`,
        `    agent_rule: ${q(k.agent)}`,
      );
    }
    if (k.reported && k.observed) {
      lines.push(
        '    case:',
        `      reported: {value: ${q(k.reported.value)}, how: ${q(k.reported.how)}}`,
        `      observed: {value: ${q(k.observed.value)}, how: ${q(k.observed.how)}}`,
        `      example: ${q(k.example ?? '')}`,
      );
    }
  }
  return new Response(`${lines.join('\n')}\n`, { headers: { 'Content-Type': 'text/yaml; charset=utf-8' } });
}
