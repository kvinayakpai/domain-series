import json,sys,glob
from catalog import answer
tot=ok=0
for f in sorted(glob.glob('../questions*.json')):
    for x in json.load(open(f)):
        if x.get('label')!='A': continue
        q=x.get('q') or x.get('question'); t=x.get('truth')
        r=answer(q); tot+=1
        good = r['decision']=='answer' and abs(float(r['value'])-float(t))<0.01
        ok+=good
        if not good: print(f.split('/')[-1], x.get('id'), q, '| truth',t,'|',{k:r.get(k) for k in('decision','value','reasons')})
print(ok,'/',tot)
