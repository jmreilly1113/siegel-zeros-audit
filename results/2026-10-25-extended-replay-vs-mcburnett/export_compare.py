import json, glob, os, collections
R='C:/Users/Work/dev/siegel/results/2026-10-21-extended-replay/runs'; N=os.path.dirname(os.path.abspath(__file__))
kp={}
for f in ['kernel-pair-sweep.jsonl','nanoda-retest.jsonl','nanoda-retest-cloud.jsonl']:
    for l in open(os.path.join(N,f)):
        j=json.loads(l)
        if j.get('export_bytes'): kp.setdefault(j['config'],set()).add(j['export_bytes'])
ca={j['config']:j for j in map(json.loads,open(os.path.join(N,'cmpall-all.jsonl')))}
ours={}; oc=collections.Counter()
for f in glob.glob(R+'/*.result.json'):
    d=json.load(open(f)); n=d['config']; oc[d.get('final_label') or d.get('outcome')]+=1
    ours[n]=(d.get('final_label') or d.get('outcome'), (d.get('export') or {}).get('export_bytes'))
same=diff=nocmp=0; dl=[]
for n,(o,b) in ours.items():
    if n not in kp or b is None: nocmp+=1; continue
    if b in kp[n]: same+=1
    else: diff+=1; dl.append((n,b,sorted(kp[n])))
print('our results',len(ours),dict(oc))
print('export bytes vs Neal: same',same,'different',diff,'not comparable',nocmp)
for x in dl[:20]: print(' diff',x)
print('in Neal cmp-all:',sum(1 for n in ours if n in ca),'accepted there:',sum(1 for n in ours if ca.get(n,{}).get('outcome')=='accepted'))
print('our non-ACCEPT_BOTH:',[(n,o) for n,(o,b) in ours.items() if o!='ACCEPT_BOTH'])
