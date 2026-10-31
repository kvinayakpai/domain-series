// The KPI library as YAML, for anyone starting a domain layer of their own. Same content as /kpis/.
import { DOMAINS } from '../../lib/kpis';

// JSON strings are valid YAML double-quoted scalars.
const q = (s: string) => JSON.stringify(s);

export function GET() {
  const lines = [
    '# Domain KPIs, x-rayed: https://kvinayakpai.github.io/domain-series/kpis/',
    '# Each KPI: what it drives, how it is usually computed, what that record cannot see,',
    '# the check that exposes the gap, the rule to give an AI agent, and Store 014\'s two numbers',
    '# (as its systems report the KPI, and as the synthetic world\'s answer key observed it).',
    'domains:',
  ];
  for (const d of DOMAINS) {
    lines.push(`  - id: ${d.id}`, `    name: ${q(d.name)}`, '    kpis:');
    for (const k of d.kpis) {
      lines.push(
        `      - id: ${k.id}`,
        `        name: ${q(k.name)}`,
        `        drives: ${q(k.drives)}`,
        `        usually_computed_from: ${q(k.computed)}`,
        `        blind_spot: ${q(k.blind)}`,
        `        domain_check: ${q(k.check)}`,
        `        agent_rule: ${q(k.agent)}`,
      );
      if (k.reported && k.observed) {
        lines.push(
          '        store_014:',
          `          reported: {value: ${q(k.reported.value)}, how: ${q(k.reported.how)}}`,
          `          observed: {value: ${q(k.observed.value)}, how: ${q(k.observed.how)}}`,
          `          example: ${q(k.example)}`,
        );
      }
    }
  }
  return new Response(`${lines.join('\n')}\n`, { headers: { 'Content-Type': 'text/yaml; charset=utf-8' } });
}
