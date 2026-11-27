"""Offline replay: apply deterministic guards (code, no model) to saved agent answers and re-score.
A guard looks only at the question text. If it fires, the answer is forced to no_record before the model's answer is used."""
import csv, json, re, sys, collections
GUARDS = {
 "window": [r"\b(january|february|march|april|july|august|september|october|november|december)\b", r"\b20(?!26\b)\d\d\b", r"\bso far (in|this) 20\d\d", r"\bin 2026\b(?!.*june)", r"\bof 2026\b", r"\blast (six|twelve|\d+) months\b", r"\bfirst (week|quarter) of\b", r"\bquarter of 2026\b", r"\bever\b", r"\bover the year\b", r"\ball of may\b", r"\ball of (may|june)\b.*\b(may)\b"],
 "identity": [r"\bwho\b", r"\bwhich (customers|shoppers|staff|cashier|supplier|households|delivery driver|segments)\b", r"\bdifferent (customers|shoppers|people)\b", r"\b(repeat rate|churn|lifetime value|age and gender|best customers)\b", r"\bhouseholds\b", r"\bwhich (staff|supplier)\b", r"\bmore than once\b.*\b(customers|shoppers|complain)"],
 "why": [r"^\s*why\b", r"\bwhat caused\b", r"\bmain reason\b", r"\bwhat inside the till\b"],
 "not_happen": [r"\babandon", r"\bvoid", r"\bcancel", r"\brefus", r"\bwalked out", r"\bleft (store|without)", r"\bwithout (buying|a bill|paying)", r"\bput (it )?back", r"\bwould have been\b", r"\btrue demand\b", r"\blost sales\b", r"\bnever\b", r"\bnot done\b", r"\bnot accept", r"\bwere told there\b", r"\bentered .* and left\b", r"\bgave up\b", r"\bsubstitut", r"\bremove[d]? from a bill\b", r"\bbefore an item was scanned\b"],
 "else": [r"\bcompetitor", r"\bweather|rainfall|temperature\b", r"\brent\b|\bstaff cost|electricity", r"\bfestival", r"\bmarket share", r"\bsatisf", r"\belasticity", r"\bother stores?\b", r"\bwholesale price", r"\bcome by car", r"\bhome-delivery|online orders?\b", r"\bprefer\b", r"\bprofitable\b|\bmaximise profit", r"\bfootfall|\bpeople visited|\bvisitors\b"],
}
def fired(q):
    ql=q.lower(); hit=[]
    for g,pats in GUARDS.items():
        if any(re.search(p,ql) for p in pats): hit.append(g)
    return hit
def run(name, qfile, scores):
    Q={q["id"]:q for q in json.load(open(qfile))}
    rows=list(csv.DictReader(open(scores)))
    agg=collections.defaultdict(collections.Counter); byg=collections.Counter(); broke=collections.Counter(); unc=collections.Counter()
    for r in rows:
        q=Q[r["id"]]; hit=fired(q["question"]); lab=r["label"]; o=r["outcome"]
        key=(("ultra" if "ultra" in r["model"] else "lightning"), r["condition"])
        agg[key][("before",lab,o)]+=1
        if lab in("N","P") and hit:
            agg[key][("after",lab,"pass")]+=1
            if o=="fabricated":
                for g in hit: byg[g]+=1
        elif lab=="A" and hit:
            agg[key][("after",lab,"over_refusal")]+=1; broke[tuple(hit)+(q["question"][:50],)]+=1
        else:
            agg[key][("after",lab,o)]+=1
        if lab in("N","P") and not hit and o=="fabricated": unc[(r["id"],q["question"][:70])]+=1
    nfab_b=sum(c[("before","N","fabricated")]+c[("before","P","fabricated")] for c in agg.values())
    nfab_a=sum(c[("after","N","fabricated")]+c[("after","P","fabricated")] for c in agg.values())
    nN=sum(sum(v for (w,l,o),v in c.items() if w=="before" and l in("N","P")) for c in agg.values())
    nA=sum(sum(v for (w,l,o),v in c.items() if w=="before" and l=="A") for c in agg.values())
    ca_b=sum(c[("before","A","correct")] for c in agg.values()); ca_a=sum(c[("after","A","correct")] for c in agg.values())
    print(f"== {name}: N+P answers {nN}, fabricated {nfab_b} -> {nfab_a}; controls {nA}, correct {ca_b} -> {ca_a}")
    print("   fabrications caught by guard:",dict(byg))
    print("   controls broken:",dict(broke) if broke else "none")
    print("   still fabricated, no guard fired (top):",[(k[0],v) for k,v in unc.most_common(8)])
run("original 76", "refusal-bench/questions.json", "refusal-bench/results/guard-input/original-scores.csv")
run("holdout 1 (43)", "refusal-bench/questions-holdout.json", "refusal-bench/results/guard-input/holdout1-scores.csv")
run("holdout 2 (40)", "refusal-bench/questions-holdout2.json", "refusal-bench/results/guard-input/holdout2-scores.csv")
