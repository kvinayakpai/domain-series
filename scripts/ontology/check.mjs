// The same SHACL check as scripts/ontology/check.py, in JavaScript: N3.js reads the Turtle and
// rdf-validate-shacl validates the June graph against the shapes. It fails unless it finds exactly the
// violations pySHACL found, and records its result in src/data/ontology-check.json. Run after check.py.
import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Parser } from 'n3';
import rdf from '@zazuko/env';
import SHACLValidator from 'rdf-validate-shacl';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const D = path.join(root, 'public', 'data', 'ontology');
const outFile = path.join(root, 'src', 'data', 'ontology-check.json');
const read = (f) => new Parser({ format: 'text/turtle' }).parse(readFileSync(path.join(D, f), 'utf8'));
const version = (p) => JSON.parse(readFileSync(path.join(root, 'node_modules', p, 'package.json'), 'utf8')).version;
const local = (t) => t.value.split('#').pop();

const shapes = rdf.dataset(read('store-014-shapes.ttl'));
const data = rdf.dataset([...read('store-014-june.ttl'), ...read('store-014.ttl')]);
const report = await new SHACLValidator(shapes, { factory: rdf }).validate(data);

// The node shape a result came from: the shape itself, or the node shape that owns the property shape.
const SH = 'http://www.w3.org/ns/shacl#';
const owner = (shape) => {
  const isNode = shapes.match(shape, rdf.namedNode('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), rdf.namedNode(`${SH}NodeShape`)).size > 0;
  return isNode ? shape : [...shapes.match(null, rdf.namedNode(`${SH}property`), shape)][0].subject;
};
const violations = report.results.map((r) => {
  const message = r.message.map((m) => m.value).join(' ');
  return { focus: local(r.focusNode), shape: local(owner(r.sourceShape)), rule: Number(message.split(':')[0].replace('Rule ', '')), message };
}).sort((a, b) => a.rule - b.rule || a.focus.localeCompare(b.focus));

const result = JSON.parse(readFileSync(outFile, 'utf8'));
const key = (v) => `${v.rule} ${v.focus} ${v.shape}`;
const py = result.shacl.python.violations.map(key);
const js = violations.map(key);
if (JSON.stringify(py) !== JSON.stringify(js)) {
  throw new Error(`JavaScript and Python disagree.\n  python: ${py.join(' | ')}\n  javascript: ${js.join(' | ')}`);
}
result.shacl.javascript = { conforms: report.conforms, count: violations.length, violations, same_as_python: true };
result.tools.n3 = version('n3');
result.tools['rdf-validate-shacl'] = version('rdf-validate-shacl');
writeFileSync(outFile, `${JSON.stringify(result, null, 2)}\n`);
console.log(`JavaScript found ${violations.length} violations, the same as pySHACL.`);
