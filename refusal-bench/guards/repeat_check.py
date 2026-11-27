"""Run every question of the given files through answer() in 10 separate processes; report any question whose output differs."""
import json, subprocess, sys, hashlib
files = sys.argv[1:]
code = ("import json,sys; sys.path.insert(0,'.'); from catalog import answer; "
        "qs=[x for f in sys.argv[1:] for x in json.load(open(f))]; "
        "print(json.dumps([[x['id'], answer(x['question'])] for x in qs], sort_keys=True, default=str))")
outs = [subprocess.run([sys.executable, "-I", "-c", code, *files], capture_output=True, text=True, cwd=".", env={"PYTHONPATH": "."}).stdout for _ in range(10)]
h = {hashlib.sha256(o.encode()).hexdigest()[:12] for o in outs}
n = len(json.loads(outs[0]))
print(f"{n} questions x 10 separate processes: {len(h)} distinct output hash(es) {sorted(h)}")
