// Writes the Store 014 ontology in open standards, from the same source as the map:
//   public/data/ontology/store-014.ttl       OWL 2 in Turtle: classes, properties, keys, code lists (SKOS),
//                                             the twelve rules and the records (PROV-O)
//   public/data/ontology/store-014-june.ttl  a small knowledge graph: Season 1's three incidents, written
//                                             as Store 014's records held them in June 2026
// The SHACL shapes (store-014-shapes.ttl) are written by hand: they are the rules as checks.
// Then run scripts/ontology/check.py (Python) and scripts/ontology/check.mjs (JavaScript).
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const data = (f) => JSON.parse(readFileSync(path.join(root, 'src', 'data', f), 'utf8'));
const O = data('ontology.json');
const retail = data('retail.json');
const ai = data('retail-ai.json');
const logistics = data('logistics.json');
const payments = data('payments.json');
const out = path.join(root, 'public', 'data', 'ontology');
mkdirSync(out, { recursive: true });

const NS = 'https://kvinayakpai.github.io/domain-series/ontology/store-014#';
const JUNE = 'https://kvinayakpai.github.io/domain-series/ontology/store-014/june#';
const lit = (s) => `"${String(s).replace(/\\/g, '\\\\').replace(/"/g, '\\"')}"`;
const en = (s) => `${lit(s)}@en`;
const dt = (s) => `"${s.length === 16 ? `${s}:00` : s}"^^xsd:dateTime`;
const int = (n) => `"${n}"^^xsd:integer`;
const dec = (n) => `"${n}"^^xsd:decimal`;
const cls = (t) => t.name.split(/\s+/).map((w) => w[0].toUpperCase() + w.slice(1)).join('');
const C = Object.fromEntries(O.things.map((t) => [t.id, `s14:${cls(t)}`]));
const KPI_NAMES = {
  lfl: 'Sales', osa: 'On-shelf availability', 'lost-sales': 'Lost sales', ira: 'Inventory record accuracy', shrink: 'Shrink',
  forecast: 'Forecast accuracy and bias', 'days-of-supply': 'Days of supply', 'fresh-waste': 'Fresh waste', 'pick-accuracy': 'Pick accuracy',
  'fill-rate': 'Fill rate', 'on-time': 'On-time arrival', otif: 'On time, in full (OTIF)', 'net-adjustments': 'Net inventory adjustments',
  'success-rate': 'Payment success rate', 'technical-declines': 'Technical decline rate', 'charged-twice': 'Double debits',
  'match-rate': 'Reconciliation match rate', 'refund-tat': 'Refund turnaround',
};

const PREFIXES = `@prefix s14: <${NS}> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
`;

// ---------- the ontology ----------
const t = [];
t.push(`# The Store 014 ontology, written from src/data/ontology.json by scripts/ontology/build.mjs. Do not edit by hand.
${PREFIXES}
<https://kvinayakpai.github.io/domain-series/ontology/store-014> a owl:Ontology ;
    dcterms:title ${en('The Store 014 ontology')} ;
    dcterms:description ${en('The things a simulated Indian supermarket sells, moves and gets paid for, how they link, the twelve rules that fix Season 1 of Why Domain Matters, and what each record sees.')} ;
    dcterms:creator ${en('Why Domain Matters (Vinayak, with his AI assistant)')} ;
    dcterms:created "2026-11-17"^^xsd:date ;
    owl:versionInfo "1.0" ;
    rdfs:seeAlso <https://kvinayakpai.github.io/domain-series/store-014-ontology/> .

# ---------- annotations ----------
s14:part a owl:AnnotationProperty ; rdfs:label ${en('part of the map')} ;
    rdfs:comment ${en('Where a thing sits on the map: the core, the truck, the shelf or the money.')} .
s14:looksAt a owl:AnnotationProperty ; rdfs:label ${en('looks at')} ;
    rdfs:comment ${en('The kind of thing in the world a record observes.')} .
s14:governs a owl:AnnotationProperty ; rdfs:label ${en('governs')} ; rdfs:comment ${en('The thing a rule is about.')} .
s14:solves a owl:AnnotationProperty ; rdfs:label ${en('solves')} ; rdfs:comment ${en('The Season 1 KPI whose blind spot a rule fixes.')} .

# ---------- the 22 things ----------`);
for (const th of O.things) {
  t.push(`${C[th.id]} a owl:Class ;
    rdfs:label ${en(th.name)} ;
    rdfs:comment ${en(th.says)} ;
    s14:part ${lit(th.group)} .`);
}
t.push(`
# Kinds of place: a taxonomy inside the ontology.
s14:Site a owl:Class ; rdfs:subClassOf s14:Place ; rdfs:label ${en('Site')} ; rdfs:comment ${en('a building known by its GLN: the warehouse or the store')} .
s14:WarehouseSlot a owl:Class ; rdfs:subClassOf s14:Place ; rdfs:label ${en('Warehouse slot')} ; rdfs:comment ${en('a pick face in the warehouse, assigned to one item')} .
s14:Shelf a owl:Class ; rdfs:subClassOf s14:Place ; rdfs:label ${en('Shelf')} ; rdfs:comment ${en('a place on the shop floor where shoppers can reach an item')} .
s14:Backroom a owl:Class ; rdfs:subClassOf s14:Place ; rdfs:label ${en('Backroom')} ; rdfs:comment ${en('the store room behind the shop floor')} .
s14:WarehouseSlot owl:disjointWith s14:Shelf , s14:Backroom . s14:Shelf owl:disjointWith s14:Backroom .
s14:Sale owl:disjointWith s14:LostSale .
s14:Product owl:disjointWith s14:Item .

# Rule 7: a case holds packs of exactly one item. Rule 11: a refund answers one debit.
s14:Case rdfs:subClassOf [ a owl:Restriction ; owl:onProperty s14:holdsItem ; owl:qualifiedCardinality "1"^^xsd:nonNegativeInteger ; owl:onClass s14:Item ] .
s14:Refund rdfs:subClassOf [ a owl:Restriction ; owl:onProperty s14:answers ; owl:qualifiedCardinality "1"^^xsd:nonNegativeInteger ; owl:onClass s14:Debit ] .
s14:PaymentAttempt rdfs:subClassOf [ a owl:Restriction ; owl:onProperty s14:forBill ; owl:qualifiedCardinality "1"^^xsd:nonNegativeInteger ; owl:onClass s14:Bill ] .

# Codes a machine can match on: one item per GTIN, one pallet per SSCC, one bill per bill number.
s14:Item owl:hasKey ( s14:gtin ) .
s14:Pallet owl:hasKey ( s14:sscc ) .
s14:Bill owl:hasKey ( s14:billId ) .
s14:Site owl:hasKey ( s14:gln ) .

# ---------- the links on the map ----------`);
for (const l of O.links) {
  t.push(`s14:${l.id} a owl:ObjectProperty ; rdfs:label ${en(l.says)} ; rdfs:domain ${C[l.from]} ; rdfs:range ${C[l.to]} .`);
}
t.push(`
# ---------- more links, behind the map ----------
s14:forBill a owl:ObjectProperty ; owl:inverseOf s14:paidBy ; rdfs:label ${en('for bill')} ; rdfs:domain s14:PaymentAttempt ; rdfs:range s14:Bill .
s14:fromAttempt a owl:ObjectProperty ; owl:inverseOf s14:mayEndIn ; rdfs:label ${en('from attempt')} ; rdfs:domain s14:Debit ; rdfs:range s14:PaymentAttempt .
s14:answers a owl:ObjectProperty ; owl:inverseOf s14:returnedBy ; rdfs:label ${en('answers')} ; rdfs:domain s14:Refund ; rdfs:range s14:Debit .
s14:aboutDebit a owl:ObjectProperty ; rdfs:label ${en('about debit')} ; rdfs:domain s14:Complaint ; rdfs:range s14:Debit .
s14:packOf a owl:ObjectProperty ; owl:inverseOf s14:comesInPack ; rdfs:label ${en('pack of')} ; rdfs:domain s14:Item ; rdfs:range s14:Product .
s14:holdsItem a owl:ObjectProperty ; rdfs:label ${en('holds item')} ; rdfs:domain s14:Case ; rdfs:range s14:Item .
s14:ofItem a owl:ObjectProperty ; rdfs:label ${en('of item')} ; rdfs:range s14:Item ;
    rdfs:comment ${en('The item a stock figure, stock change, demand, forecast, order or sale is about.')} .
s14:atPlace a owl:ObjectProperty ; rdfs:label ${en('at place')} ; rdfs:range s14:Place .
s14:within a owl:ObjectProperty ; rdfs:label ${en('within')} ; rdfs:domain s14:Place ; rdfs:range s14:Site .
s14:fromSlot a owl:ObjectProperty ; rdfs:label ${en('from slot')} ; rdfs:domain s14:Pick ; rdfs:range s14:WarehouseSlot .
s14:assignedItem a owl:ObjectProperty ; rdfs:label ${en('assigned item')} ; rdfs:domain s14:WarehouseSlot ; rdfs:range s14:Item .
s14:byCustomer a owl:ObjectProperty ; rdfs:label ${en('by customer')} ; rdfs:range s14:Customer .
s14:scoredAgainst a owl:ObjectProperty ; rdfs:label ${en('scored against')} ; rdfs:domain s14:Forecast .
s14:confirmedBy a owl:ObjectProperty ; rdfs:label ${en('confirmed by')} ; rdfs:domain s14:Pick ; rdfs:range s14:ScanMethod .
s14:checkedBy a owl:ObjectProperty ; rdfs:label ${en('checked by')} ; rdfs:domain s14:Receiving ; rdfs:range s14:ScanMethod .
s14:basis a owl:ObjectProperty ; rdfs:label ${en('basis')} ; rdfs:domain s14:Stock ; rdfs:range s14:StockBasis .
s14:tillStatus a owl:ObjectProperty ; rdfs:label ${en('till status')} ; rdfs:domain s14:PaymentAttempt ; rdfs:range s14:TillStatus .
s14:finalStatus a owl:ObjectProperty ; rdfs:label ${en('final status')} ; rdfs:domain s14:PaymentAttempt ; rdfs:range s14:UpiStatus ;
    rdfs:comment ${en("UPI's final status for a payment attempt: the one that decides.")} .
s14:fromRecord a owl:ObjectProperty ; rdfs:subPropertyOf prov:wasDerivedFrom ; rdfs:label ${en('from record')} ; rdfs:range s14:Record ;
    rdfs:comment ${en('The record a fact in the knowledge graph came from.')} .

# ---------- codes and values ----------
s14:gtin a owl:DatatypeProperty , owl:FunctionalProperty ; rdfs:label ${en('GTIN')} ; rdfs:domain s14:Item ; rdfs:range xsd:string ;
    rdfs:comment ${en('The GS1 trade item number printed on the pack.')} .
s14:sscc a owl:DatatypeProperty , owl:FunctionalProperty ; rdfs:label ${en('SSCC')} ; rdfs:domain s14:Pallet ; rdfs:range xsd:string ;
    rdfs:comment ${en('The GS1 serial shipping container code on the pallet label.')} .
s14:gln a owl:DatatypeProperty ; rdfs:label ${en('GLN')} ; rdfs:domain s14:Site ; rdfs:range xsd:string ; rdfs:comment ${en('The GS1 global location number of a site.')} .
s14:rrn a owl:DatatypeProperty ; rdfs:label ${en('RRN')} ; rdfs:range xsd:string ; rdfs:comment ${en('The UPI retrieval reference number of a payment.')} .
s14:billId a owl:DatatypeProperty ; rdfs:label ${en('bill number')} ; rdfs:domain s14:Bill ; rdfs:range xsd:string .
s14:carriesBillId a owl:DatatypeProperty ; rdfs:label ${en('carries bill number')} ; rdfs:domain s14:PaymentAttempt ; rdfs:range xsd:string ;
    rdfs:comment ${en('The bill number the UPI request itself carried, so the credit can be matched to the bill.')} .
s14:code a owl:DatatypeProperty ; rdfs:label ${en('code')} ; rdfs:range xsd:string ; rdfs:comment ${en("A system's own code: a SKU, a slot, an order or a receipt number.")} .
s14:tender a owl:DatatypeProperty ; rdfs:label ${en('tender')} ; rdfs:domain s14:PaymentAttempt ; rdfs:range xsd:string .
s14:quantity a owl:DatatypeProperty ; rdfs:label ${en('quantity')} ; rdfs:range xsd:integer ; rdfs:comment ${en('Packs (units). Negative for a stock change that takes packs off.')} .
s14:cases a owl:DatatypeProperty ; rdfs:label ${en('cases')} ; rdfs:range xsd:integer .
s14:packsPerCase a owl:DatatypeProperty ; rdfs:label ${en('packs per case')} ; rdfs:domain s14:Item ; rdfs:range xsd:integer .
s14:amountInr a owl:DatatypeProperty ; rdfs:label ${en('amount (INR)')} ; rdfs:range xsd:decimal .
s14:perDay a owl:DatatypeProperty ; rdfs:label ${en('per day')} ; rdfs:domain s14:Forecast ; rdfs:range xsd:decimal .
s14:at a owl:DatatypeProperty ; rdfs:label ${en('at')} ; rdfs:range xsd:dateTime ; rdfs:comment ${en('When it happened, or when it was seen.')} .
s14:windowStart a owl:DatatypeProperty ; rdfs:label ${en('window starts')} ; rdfs:domain s14:Shipment ; rdfs:range xsd:dateTime .
s14:windowEnd a owl:DatatypeProperty ; rdfs:label ${en('window ends')} ; rdfs:domain s14:Shipment ; rdfs:range xsd:dateTime .
s14:reason a owl:DatatypeProperty ; rdfs:label ${en('reason')} ; rdfs:domain s14:StockChange ; rdfs:range xsd:string .
s14:method a owl:DatatypeProperty ; rdfs:label ${en('method')} ; rdfs:range xsd:string ; rdfs:comment ${en('How a forecast or an estimate was made.')} .

# ---------- code lists (SKOS) ----------
s14:ScanMethod a owl:Class ; rdfs:subClassOf skos:Concept ; rdfs:label ${en('Scan method')} .
s14:StockBasis a owl:Class ; rdfs:subClassOf skos:Concept ; rdfs:label ${en('Stock basis')} .
s14:TillStatus a owl:Class ; rdfs:subClassOf skos:Concept ; rdfs:label ${en('Till status')} .
s14:UpiStatus a owl:Class ; rdfs:subClassOf skos:Concept ; rdfs:label ${en('UPI status')} .
s14:PackCodeScan a s14:ScanMethod ; skos:prefLabel ${en('pack code scan')} ; skos:definition ${en('A scan of the GTIN on the pack or the case.')} .
s14:SlotLabelScan a s14:ScanMethod ; skos:prefLabel ${en('slot label scan')} ; skos:definition ${en("A scan of the warehouse slot's label: it proves where the picker stood.")} .
s14:PalletLabelScan a s14:ScanMethod ; skos:prefLabel ${en('pallet label scan')} ; skos:definition ${en('A scan of the SSCC on the pallet label, matched to the shipping notice.')} .
s14:Seen a s14:StockBasis ; skos:prefLabel ${en('seen')} ; skos:definition ${en('Stock someone saw: a shelf audit, a count, or a sale at the till.')} .
s14:Believed a s14:StockBasis ; skos:prefLabel ${en('believed')} ; skos:definition ${en('Stock the books believe: the last count, plus receipts, minus sales and write-offs.')} .
s14:Approved a s14:TillStatus ; skos:prefLabel ${en('approved')} .
s14:Declined a s14:TillStatus ; skos:prefLabel ${en('declined')} .
s14:Timeout a s14:TillStatus ; skos:prefLabel ${en('timeout')} ; skos:definition ${en('No answer in time. Not known yet, not failed.')} .
s14:Success a s14:UpiStatus ; skos:prefLabel ${en('success')} .
s14:Failure a s14:UpiStatus ; skos:prefLabel ${en('failure')} .

# ---------- the twelve rules, and the Season 1 KPIs they fix ----------
s14:Rule a owl:Class ; rdfs:label ${en('Rule')} .
s14:Kpi a owl:Class ; rdfs:label ${en('Season 1 KPI')} .`);
for (const [id, name] of Object.entries(KPI_NAMES)) t.push(`s14:kpi-${id} a s14:Kpi ; rdfs:label ${en(name)} .`);
for (const r of O.rules) {
  const gov = r.on.map((o) => (o === 'records' ? 's14:Record' : C[o])).join(' , ');
  const solves = r.solves.length ? ` ;\n    s14:solves ${r.solves.map((s) => `s14:kpi-${s}`).join(' , ')}` : '';
  t.push(`s14:rule-${r.n} a s14:Rule ;
    rdfs:label ${en(`Rule ${r.n}`)} ;
    rdfs:comment ${en(r.text)} ;
    s14:governs ${gov}${solves} .`);
}
t.push(`
# ---------- records: who saw what (W3C PROV-O) ----------
s14:Record a owl:Class ; rdfs:subClassOf prov:Entity ; rdfs:label ${en('Record')} ;
    rdfs:comment ${en('A record either looks at the world or copies another record (rule 12).')} .
s14:till-lines a s14:Record ; rdfs:label ${en('till lines')} ; s14:looksAt s14:Shelf ; rdfs:comment ${en('A sale proves the pack was on the shelf. No sale proves nothing.')} .
s14:stock-counts a s14:Record ; rdfs:label ${en('stock counts')} ; s14:looksAt s14:Shelf , s14:Backroom .
s14:shelf-audits a s14:Record ; rdfs:label ${en('shelf audits')} ; s14:looksAt s14:Shelf .
s14:warehouse-slot-counts a s14:Record ; rdfs:label ${en('warehouse slot counts')} ; s14:looksAt s14:WarehouseSlot .
s14:upi-report a s14:Record ; rdfs:label ${en("UPI's report")} ; s14:looksAt s14:Debit ; rdfs:comment ${en('Whether the customer was debited and the store credited.')} .
s14:pick-confirmations a s14:Record ; rdfs:label ${en('pick confirmations')} ; s14:looksAt s14:WarehouseSlot ; rdfs:comment ${en('Where the picker stood, not what they took.')} .
s14:book-stock a s14:Record ; rdfs:label ${en('book stock')} ; prov:wasDerivedFrom s14:goods-receipts , s14:till-lines , s14:stock-counts .
s14:shipping-notice a s14:Record ; rdfs:label ${en('shipping notice')} ; prov:wasDerivedFrom s14:pick-confirmations .
s14:pallet-labels a s14:Record ; rdfs:label ${en('pallet labels')} ; prov:wasDerivedFrom s14:shipping-notice .
s14:goods-receipts a s14:Record ; rdfs:label ${en('goods receipts')} ; prov:wasDerivedFrom s14:shipping-notice .
s14:settlements a s14:Record ; rdfs:label ${en('settlements')} ; prov:wasDerivedFrom s14:upi-report .
s14:till-payments a s14:Record ; rdfs:label ${en('till payments')} ; prov:wasDerivedFrom s14:upi-report ;
    rdfs:comment ${en("The provider's answer, or the till's own timeout.")} .
s14:forecasts a s14:Record ; rdfs:label ${en('forecasts')} ; prov:wasDerivedFrom s14:till-lines .
`);
writeFileSync(path.join(out, 'store-014.ttl'), t.join('\n'));

// ---------- June: Season 1's three incidents, as the records held them ----------
const st = logistics.story;
const line = st.line;
const pick = st.picks.find((p) => p.line === line.line);
const grn22 = st.receipt;
const pallet22 = st.pallets.find((p) => p.sscc === line.sscc);
const grn9 = retail.records.receipts.find((r) => r.received_ts.startsWith('2026-06-09') && r.sku_booked === 'ATTA-WW-5KG');
const ep = retail.story.episode;
const audit = ai.tests.domain[1].failing.find((a) => a.sku === 'ATTA-WW-5KG');
const fc = ai.forecast.made_5kg.find((m) => m.date === '2026-06-10');
const fcMethod = retail.records.forecasts.find((f) => f.sku === 'ATTA-WW-5KG').method;
const dc = st.dc_adjustments;
const store = st.corrections;
const gtin1kg = logistics.story.lines_on_truck?.find?.((x) => x.sku === 'ATTA-WW-1KG')?.gtin
  ?? JSON.stringify(logistics).match(/"sku":"ATTA-WW-1KG","gtin":"(\d+)"/)[1];
const scene = payments.story.scene;
const [upi, card] = scene.attempts;
const settle = payments.records.settlements.find((s) => s.settlement_date === '2026-06-21');
const id = (s) => s.replace(/[^A-Za-z0-9-]/g, '-');

const j = [];
j.push(`# June 2026 at Store 014: Season 1's three incidents, written as the store's records held them.
# Written from src/data by scripts/ontology/build.mjs. Do not edit by hand.
${PREFIXES}@prefix june: <${JUNE}> .

# ---------- items, places ----------
june:atta a s14:Product ; rdfs:label ${en('Whole-wheat atta')} ; s14:comesInPack june:atta-5kg , june:atta-1kg .
june:atta-5kg a s14:Item ; rdfs:label ${en(logistics.hero.name)} ; s14:gtin ${lit(logistics.hero.gtin)} ; s14:code ${lit(logistics.hero.sku)} ; s14:packsPerCase ${int(logistics.hero.case_units)} .
june:atta-1kg a s14:Item ; rdfs:label ${en(logistics.one_kg.name)} ; s14:gtin ${lit(gtin1kg)} ; s14:code ${lit(logistics.one_kg.sku)} ; s14:packsPerCase ${int(logistics.one_kg.case_units)} .
june:warehouse a s14:Site ; rdfs:label ${en('The warehouse')} ; s14:gln ${lit(st.shipment.from_gln)} .
june:store-014 a s14:Site ; rdfs:label ${en('Store 014, Jayanagar, Bengaluru')} ; s14:gln ${lit(st.shipment.to_gln)} .
june:slot-${logistics.slots['ATTA-WW-5KG']} a s14:WarehouseSlot ; s14:code ${lit(logistics.slots['ATTA-WW-5KG'])} ; s14:within june:warehouse ; s14:assignedItem june:atta-5kg .
june:slot-${logistics.slots['ATTA-WW-1KG']} a s14:WarehouseSlot ; s14:code ${lit(logistics.slots['ATTA-WW-1KG'])} ; s14:within june:warehouse ; s14:assignedItem june:atta-1kg .
june:shelf-atta-5kg a s14:Shelf ; rdfs:label ${en('The 5 kg atta bay')} ; s14:within june:store-014 .

# ---------- the shelf, 9-12 June: 5 kg atta in the wrong bay ----------
june:${id(grn9.grn_id)} a s14:Receiving ; s14:code ${lit(grn9.grn_id)} ; s14:at ${dt(grn9.received_ts)} ;
    s14:checkedBy s14:PalletLabelScan ; s14:fromRecord s14:goods-receipts ;
    rdfs:comment ${en(`${grn9.units_booked} bags of 5 kg atta, booked by ${grn9.receipt_method}. They went behind the rice, in the wrong bay.`)} .
june:book-0610 a s14:Stock ; s14:ofItem june:atta-5kg ; s14:quantity ${int(ep.book_on_hand_max)} ; s14:at ${dt(ep.start)} ;
    s14:basis s14:Believed ; s14:fromRecord s14:book-stock ;
    rdfs:comment ${en('What the books showed when the shelf ran out. The book stock has no place.')} .
june:audit-0612 a s14:Stock ; s14:ofItem june:atta-5kg ; s14:atPlace june:shelf-atta-5kg ; s14:quantity ${int(0)} ; s14:at ${dt(audit.audit_ts.slice(0, 16))} ;
    s14:basis s14:Seen ; s14:fromRecord s14:shelf-audits ;
    rdfs:comment ${en(`A routine shelf check found the bay empty, with ${audit.book} bags on the books.`)} .
june:recorded-sales-5kg a s14:Sale ; s14:ofItem june:atta-5kg ; s14:fromRecord s14:till-lines ;
    rdfs:comment ${en('Recorded sales of 5 kg atta: demand met while the shelf had stock.')} .
june:forecast-0610 a s14:Forecast ; s14:ofItem june:atta-5kg ; s14:at ${dt('2026-06-10T00:00')} ; s14:perDay ${dec(fc.naive)} ;
    s14:method ${lit(fcMethod)} ; s14:scoredAgainst june:recorded-sales-5kg ; s14:fromRecord s14:forecasts .

# ---------- the truck, 22-26 June: 1 kg packs on a 5 kg pallet line ----------
june:${id(line.order_id)} a s14:StoreOrder ; s14:code ${lit(line.order_id)} ; s14:ofItem june:atta-5kg ; s14:cases ${int(pick.cases_ordered)} ;
    s14:pickedAs june:pick-${id(line.shipment_id)}-${line.line} .
june:pick-${id(line.shipment_id)}-${line.line} a s14:Pick ; s14:at ${dt(pick.pick_ts)} ; s14:fromSlot june:slot-${pick.slot} ; s14:cases ${int(pick.cases_confirmed)} ;
    s14:confirmedBy s14:SlotLabelScan ; s14:takesCase june:cases-${id(line.shipment_id)}-${line.line} ; s14:fromRecord s14:pick-confirmations .
june:cases-${id(line.shipment_id)}-${line.line} a s14:Case ; s14:holdsItem june:atta-5kg ; s14:cases ${int(line.cases)} ; s14:quantity ${int(line.units)} ;
    s14:loadedOn june:pallet-${pallet22.sscc} ; s14:fromRecord s14:shipping-notice ;
    rdfs:comment ${en('As the shipping notice says. No record read the code on these cases.')} .
june:pallet-${pallet22.sscc} a s14:Pallet ; s14:sscc ${lit(pallet22.sscc)} ; s14:cases ${int(pallet22.cases)} ; s14:carriedBy june:${id(line.shipment_id)} ;
    s14:fromRecord s14:pallet-labels ; rdfs:comment ${en(`${pallet22.weight_check}.`)} .
june:${id(line.shipment_id)} a s14:Shipment ; s14:code ${lit(line.shipment_id)} ; s14:windowStart ${dt(st.shipment.slot_start)} ; s14:windowEnd ${dt(st.shipment.slot_end)} ;
    s14:at ${dt(st.shipment.arrived_ts)} ; s14:endsIn june:${id(grn22.grn_id)} .
june:${id(grn22.grn_id)} a s14:Receiving ; s14:code ${lit(grn22.grn_id)} ; s14:at ${dt(grn22.received_ts)} ;
    s14:checkedBy s14:PalletLabelScan ; s14:fromRecord s14:goods-receipts .`);
for (const [k, a] of dc.entries()) {
  j.push(`june:dc-correction-${k + 1} a s14:StockChange ; s14:ofItem june:${a.sku === 'ATTA-WW-5KG' ? 'atta-5kg' : 'atta-1kg'} ; s14:atPlace june:slot-${a.slot} ;
    s14:quantity ${int(a.units)} ; s14:at ${dt(a.adjusted_ts)} ; s14:reason ${lit(a.reason)} ; s14:fromRecord s14:warehouse-slot-counts .`);
}
for (const [k, c] of store.entries()) {
  j.push(`june:store-correction-${k + 1} a s14:StockChange ; s14:ofItem june:${c.sku === 'ATTA-WW-5KG' ? 'atta-5kg' : 'atta-1kg'} ; s14:atPlace june:store-014 ;
    s14:quantity ${int(c.adjustment)} ; s14:at ${dt(c.count_ts)} ; s14:fromRecord s14:stock-counts ;
    rdfs:comment ${en(`Count after ${c.trigger}: the books said ${c.book_before}, the count found ${c.counted}. No reason recorded.`)} .`);
}
j.push(`
# ---------- the money, 20-28 June: a timeout the bank had already paid ----------
june:bill-${scene.bill_id} a s14:Bill ; s14:billId ${lit(scene.bill_id)} ; s14:amountInr ${dec(scene.amount_inr)} ;
    s14:paidBy june:attempt-${scene.bill_id}-1 , june:attempt-${scene.bill_id}-2 .
june:attempt-${scene.bill_id}-1 a s14:PaymentAttempt ; s14:forBill june:bill-${scene.bill_id} ; s14:tender ${lit(upi.tender)} ; s14:at ${dt(upi.ts)} ;
    s14:amountInr ${dec(upi.amount_inr)} ; s14:tillStatus s14:Timeout ; s14:mayEndIn june:debit-${scene.rrn} ; s14:fromRecord s14:till-payments ;
    rdfs:comment ${en(`The till said "${upi.till_status}". The UPI request carried no bill number.`)} .
june:attempt-${scene.bill_id}-2 a s14:PaymentAttempt ; s14:forBill june:bill-${scene.bill_id} ; s14:tender ${lit(card.tender)} ; s14:at ${dt(card.ts)} ;
    s14:amountInr ${dec(card.amount_inr)} ; s14:tillStatus s14:Approved ; s14:mayEndIn june:debit-${scene.bill_id}-card ; s14:fromRecord s14:till-payments .
june:debit-${scene.rrn} a s14:Debit ; s14:rrn ${lit(scene.rrn)} ; s14:fromAttempt june:attempt-${scene.bill_id}-1 ; s14:at ${dt(scene.paid_ts)} ;
    s14:amountInr ${dec(scene.amount_inr)} ; s14:creditedIn june:settlement-${settle.settlement_date} ; s14:fromRecord s14:upi-report .
june:debit-${scene.bill_id}-card a s14:Debit ; s14:fromAttempt june:attempt-${scene.bill_id}-2 ; s14:at ${dt(card.ts)} ; s14:amountInr ${dec(card.amount_inr)} .
june:settlement-${settle.settlement_date} a s14:Settlement ; s14:at ${dt(`${settle.settlement_date}T00:00`)} ; s14:amountInr ${dec(settle.gross_inr)} ;
    s14:fromRecord s14:settlements ; rdfs:comment ${en(`${settle.upi_credits} UPI credits from the day before.`)} .
june:complaint-${scene.bill_id} a s14:Complaint ; s14:at ${dt(scene.complaint.complaint_ts)} ; s14:aboutDebit june:debit-${scene.rrn} ;
    s14:asksFor june:refund-${scene.bill_id} ; rdfs:comment ${en(scene.complaint.kind)} .
june:refund-${scene.bill_id} a s14:Refund ; s14:answers june:debit-${scene.rrn} ; s14:at ${dt(scene.refunded_ts)} ; s14:amountInr ${dec(scene.amount_inr)} ;
    rdfs:comment ${en(scene.complaint.resolution)} .
`);
writeFileSync(path.join(out, 'store-014-june.ttl'), j.join('\n'));
console.log('wrote public/data/ontology/store-014.ttl and store-014-june.ttl');
