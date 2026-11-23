"""Repeat the packs test: one NVIDIA model, the Opus and Sonnet packs, with and without the 'no record' line,
TRIES times each. Uses owl-packs-test/run.py unchanged. Usage: python3 run_repeat.py <results folder>"""
import importlib.util, json, os, re, sys
from pathlib import Path

spec = importlib.util.spec_from_file_location("runner", Path(__file__).resolve().parent.parent / "owl-packs-test" / "run.py")
runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
tries = int(os.environ.get("TRIES", "3"))
packs = os.environ.get("PACKS", "auto-opus,auto-sonnet").split(",")
tag = re.sub(r"[^a-z0-9.]+", "_", runner.MODELS["nim"]["name"].lower())
for t in range(1, tries + 1):
    for pack in packs:
        for rule in (False, True):
            name = f"{tag}-{pack}{'-rule' if rule else ''}-t{t}"
            print("running", name, flush=True)
            try:
                rec = runner.run_one("nim", pack, rule)
            except Exception as e:
                rec = {"model": "nim", "pack": pack, "rule_line": rule, "error": str(e)[:300]}
            rec["try"] = t
            (out / f"{name}.json").write_text(json.dumps(rec, indent=2))
            print("done", name, rec.get("seconds"), rec.get("error", ""), flush=True)
