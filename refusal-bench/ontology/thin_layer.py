"""Thin model layer for the Store 014 resolver. The model may only REWRITE a question into the resolver's own words; it never answers,
never writes SQL and never sees data. Code decides everything else.

Flow (answer_with_model):
  1. The resolver answers the original question. If it answers, or refuses because of the registry (not recorded, stand-in, dates not
     covered), that is final: the model is never called. An unanswerable question cannot be rewritten into an answerable one.
  2. Only when the refusal is "words not defined" or "product not named", the model is asked for JSON:
        {"canonical": "<question in defined words>", "mappings": [{"from": "<word in the question>", "to": "<defined word>"}]}
  3. Deterministic verification of the rewrite (verify()). It is accepted only if ALL hold:
        - the canonical question is one line, short, and the resolver ANSWERS it (registry clean on both texts)
        - every word of the original missing from the canonical is a filler word, or the "from" of an approved mapping
        - every word of the canonical missing from the original is either a function word or the "to" of an approved mapping
        - an approved mapping is a pair in synonyms.json (reviewed by a person) or a typo: one letter added, dropped, changed or two
          adjacent letters swapped, into a word the ontology defines, with exactly one candidate
        - every number, id, time, month, year, comparator and negation of the original is in the canonical, and the canonical adds none
        - the aggregate (count, total, average, highest, lowest) is the same
  4. A mapping that is not approved is not used. It is written to synonym-proposals.json for a person to review; once approved the
     same question answers deterministically without the model.
  5. Every rewrite is stored in rewrite-cache.json keyed by the question, so a repeated question is answered from the cache.
"""
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import resolver  # noqa: E402
from resolver import answer, registry_layer, stem, tokenize  # noqa: E402

SYNONYMS = HERE / "synonyms.json"
PROPOSALS = HERE / "synonym-proposals.json"
CACHE = HERE / "rewrite-cache.json"

FILLER = set("""please kindly tell me us can could would you give show let know need want like i we us hey hi hello thanks thank pls just so really actually
ok okay um uh well quickly also then now there here any some get got is are was were do does did the a an of to for in on at by with from and as it its that this
what whats which how many much about regarding tell store 014 s""".split())
FUNCTION = set("""a an the of in on at by for from to with and or is are was were be been do does did has have had how many much what which total number""".split())
NEGATIONS = {"not", "never", "no", "none", "nothing", "nobody", "without", "except", "only", "unless", "neither", "nor", "n't", "cannot", "cant"}
COMPARE = {"above", "below", "over", "under", "more", "less", "least", "most", "before", "after", "between", "than", "within", "since", "until", "during", "per", "each", "every", "or"}
AGG_CLASSES = {"count": {"many", "number", "count"}, "sum": {"total", "sum", "altogether"}, "avg": {"average", "mean", "typical"},
               "max": {"highest", "largest", "biggest", "maximum", "peak", "most"}, "min": {"lowest", "smallest", "minimum", "least", "fewest"}}


def agg_classes(text):
    toks = {stem(t) for t in tokenize(text)}
    return {c for c, ws in AGG_CLASSES.items() if any(stem(w) in toks for w in ws)}


def approved_pairs():
    return {(a.lower(), b.lower()) for a, b in json.loads(SYNONYMS.read_text())["approved"]} if SYNONYMS.exists() else set()


def defined_words():
    """every word the ontology defines: cue words, code-value words, product words, column-name words, glue words"""
    O = resolver.onto()
    words = set(O.glue)
    for t in O.tables.values():
        for c in t["nouns"]:
            words |= {stem(w) for w in c}
        for cname, c in t["cols"].items():
            words |= {stem(w) for w in cname.split("_")}
            for cs in c["cues"]:
                words |= {stem(w) for w in cs}
            for ph in c["values"]:
                words |= {stem(w) for w in tokenize(ph)}
    for _, cs, label in O.products:
        for c in cs:
            words |= {stem(w) for w in c}
    for _, _, _, fc, _ in O.flags:
        for c in fc:
            words |= {stem(w) for w in c}
    return words


def one_edit(a, b):
    """True when b is a with one letter added, dropped or changed, or two adjacent letters swapped"""
    if a == b:
        return False
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        diff = [i for i in range(la) if a[i] != b[i]]
        if len(diff) == 1:
            return True
        return len(diff) == 2 and diff[1] == diff[0] + 1 and a[diff[0]] == b[diff[1]] and a[diff[1]] == b[diff[0]]
    s, l = (a, b) if la < lb else (b, a)
    return any(l[:i] + l[i + 1:] == s for i in range(len(l)))


def typo_target(word, vocab):
    w = stem(word)
    if len(w) < 5:
        return None
    cands = sorted({v for v in vocab if len(v) >= 5 and one_edit(w, v)})
    return cands[0] if len(cands) == 1 else None


def constraint_tokens(text):
    toks = tokenize(text)
    out = set()
    for t in toks:
        if re.search(r"\d", t) or t in NEGATIONS or t in COMPARE or t in resolver.MONTHS:
            out.add(stem(t))
    return out


def verify(original, canonical, mappings):
    """Return (ok, reason). Deterministic. The mappings are the model's claims about which words it replaced."""
    if not isinstance(canonical, str) or "\n" in canonical or len(canonical) > 300 or not canonical.strip():
        return False, "the rewrite is not a single short question"
    if canonical.strip().upper() == "CANNOT":
        return False, "the model could not express the question in defined words"
    o_t, c_t = tokenize(original), tokenize(canonical)
    o_s, c_s = [stem(t) for t in o_t], [stem(t) for t in c_t]
    pairs = approved_pairs(); vocab = defined_words()
    accepted_from, accepted_to, rejected = {}, set(), []
    for m in mappings if isinstance(mappings, list) else []:
        try:
            fr, to = stem(str(m["from"]).lower()), stem(str(m["to"]).lower())
        except Exception:  # noqa: BLE001
            return False, "malformed mapping"
        if (fr, to) in {(stem(a), stem(b)) for a, b in pairs}:
            accepted_from[fr] = to; accepted_to.add(to)
        elif to in vocab and typo_target(fr, vocab) == to:
            accepted_from[fr] = to; accepted_to.add(to)
        else:
            rejected.append((fr, to))
    if rejected:
        return False, "not an approved meaning: " + ", ".join(f"'{a}' as '{b}'" for a, b in rejected)
    # every original word must survive, be filler, or be an accepted mapping
    c_set, o_set = set(c_s), set(o_s)
    for t in o_s:
        if t in c_set or t in FILLER or stem(t) in FILLER or t in accepted_from or t in vocab and t in c_set:
            continue
        if t in {"2026", "014"}:
            continue
        return False, f"'{t}' from the question is not in the rewrite and is not an approved filler or mapping"
    for t in c_s:
        if t in o_set or t in FUNCTION or t in accepted_to or t in {"2026"} and "2026" in o_set:
            continue
        return False, f"the rewrite adds '{t}', which is not in the question"
    if constraint_tokens(original) != constraint_tokens(canonical):
        return False, "numbers, dates, comparisons or negations differ between the question and the rewrite"
    ao, ac = agg_classes(original), agg_classes(canonical)
    if ao != ac and not (not ao and ac <= {"count", "sum"}):
        return False, f"the aggregate changed from {sorted(ao)} to {sorted(ac)}"
    return True, "ok"


def prompt_for(question):
    O = resolver.onto()
    kinds = "; ".join(f"{t['label']} ({t['grain']})" for t in O.tables.values())
    products = "; ".join(l for _, _, l in O.products)
    return (
        "You rewrite a question about one grocery store's records into a plain, standard form. You do not answer it.\n"
        "Use only words the question already contains, plus function words (how many, the, of, in, was). You may fix a misspelt word or replace a word by a "
        "word with the same meaning that these records define. Never add, drop or change a number, date, product, status, comparison or 'not'. Never change "
        "count to total or average. Keep 'June 2026' only if the question says it.\n"
        f"Record kinds: {kinds}.\nProducts: {products}.\n"
        "Examples of standard form: 'How many units of toned milk were sold in June 2026?'; 'How many cash payment attempts were approved in June 2026?'; "
        "'What was the total revenue from sugar in June 2026?'; 'How many shipments were dispatched before 05:00 in June 2026?'.\n"
        'Reply with JSON only: {"canonical": "<the question in standard form>", "mappings": [{"from": "<a word you replaced>", "to": "<the word you used>"}]}. '
        'If you cannot, reply {"canonical": "CANNOT", "mappings": []}.\n'
        f"Question: {question}")


def model_rewrite(question):
    """Call an OpenAI-compatible chat endpoint (NVIDIA-hosted by default). Temperature 0. Returns parsed JSON or None."""
    import requests
    base = os.environ.get("BASE_URL", "https://integrate.api.nvidia.com/v1")
    model = os.environ["MODEL"]
    for attempt in range(6):
        try:
            r = requests.post(f"{base}/chat/completions", timeout=120, headers={"Authorization": "Bearer " + os.environ["NVIDIA_API_KEY"]},
                              json={"model": model, "messages": [{"role": "user", "content": prompt_for(question)}], "temperature": 0, "max_tokens": 600})
            if r.status_code in (429, 503, 529):
                time.sleep(min(30, 5 * (attempt + 1))); continue
            r.raise_for_status()
            text = r.json()["choices"][0]["message"]["content"] or ""
            m = re.search(r"\{.*\}", text, re.S)
            return json.loads(m.group(0)) if m else None
        except Exception:  # noqa: BLE001
            time.sleep(3)
    return None


def _load(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def answer_with_model(question, rewriter=model_rewrite, use_cache=True, write=True):
    """Final answer plus an audit record. The resolver's decision on the original question is final unless it refused for undefined words."""
    first = answer(question)
    audit = {"question": question, "first": first["decision"], "model_called": False}
    if first["decision"] == "answer":
        return {**first, "via": "resolver", "audit": audit}
    msg = first.get("message") or ""
    hard, proxy = registry_layer(question)
    needs_model = (not hard and not proxy and first["decision"] == "no_record"
                   and ("not defined for this record kind" in msg or "not named uniquely" in msg or "names more than one product" in msg or "does not ask for" in msg))
    if not needs_model:
        return {**first, "via": "resolver", "audit": audit}
    key = hashlib.sha256(question.encode()).hexdigest()[:16]
    cache = _load(CACHE, {}) if use_cache else {}
    if key in cache:
        reply = cache[key]; audit["from_cache"] = True
    else:
        reply = rewriter(question); audit["model_called"] = True
        if write and use_cache and reply is not None:
            cache[key] = reply; CACHE.write_text(json.dumps(cache, indent=1, sort_keys=True))
    if not isinstance(reply, dict):
        return {**first, "via": "resolver", "audit": {**audit, "rewrite": "no usable reply"}}
    canonical, mappings = reply.get("canonical"), reply.get("mappings", [])
    audit.update(canonical=canonical, mappings=mappings)
    ok, why = verify(question, canonical, mappings)
    audit["verified"] = ok; audit["why"] = why
    if not ok:
        # a mapping that was refused only because nobody has approved it is queued for review, never used
        if write and isinstance(mappings, list) and mappings:
            props = _load(PROPOSALS, {"proposals": []})
            for m in mappings:
                item = {"from": str(m.get("from", "")).lower(), "to": str(m.get("to", "")).lower()}
                if item["from"] and item not in props["proposals"] and (item["from"], item["to"]) not in approved_pairs():
                    props["proposals"].append(item)
            PROPOSALS.write_text(json.dumps(props, indent=1, sort_keys=True))
        return {**first, "via": "resolver", "audit": audit}
    second = answer(canonical)
    audit["second"] = second["decision"]
    if second["decision"] != "answer":
        return {**first, "via": "resolver", "audit": audit}
    return {**second, "via": "model rewrite, verified", "message": f"Read as: {canonical}" + (f" {second['message']}" if second.get("message") else ""), "audit": audit}


if __name__ == "__main__":
    r = answer_with_model(" ".join(sys.argv[1:]))
    print(json.dumps({k: r.get(k) for k in ("decision", "value", "message", "via", "audit")}, indent=1, default=str))
