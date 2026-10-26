import json
big='OrdinaryTwoPointCorrelations JointDickman SurfaceImmersion ContinuumCoulombHardness InvariantIsing FalconerAllDimensions DefocusingNLS PolycyclicRecognition OstmannComplete PattersonFirstMoment'.split()
ca={j['config']:j for j in map(json.loads,open('cmpall-all.jsonl'))}
kp={}
for l in open('kernel-pair-sweep.jsonl'):
    j=json.loads(l); kp[j['config']]=j
rt={}
for f in ['nanoda-retest.jsonl','nanoda-retest-cloud.jsonl']:
    for l in open(f):
        j=json.loads(l); rt.setdefault(j['config'],[]).append(j)
for b in big:
    c=ca.get(b,{}); k=kp.get(b,{})
    print(b,'| cmp:',c.get('outcome'),'nanoda_cfg',c.get('nanoda'),'build',c.get('build_s'),'cmp',c.get('cmp_s'),
      '| pair: lean',k.get('lean_rc'),(k.get('lean_verdict') or '')[:30],'nanoda',k.get('nanoda_rc'),k.get('nanoda_wall_s'),k.get('nanoda_rss_gib'),(k.get('nanoda_err') or '')[:60],
      '| retest:',[(r.get('nanoda_commit'),r.get('nanoda_rc'),r.get('wall_s')) for r in rt.get(b,[])])
print(len(kp), sum(1 for j in kp.values() if j.get('lean_rc')==0), sum(1 for j in kp.values() if j.get('nanoda_rc')==0))
print('cmp nanoda-true configs', [k for k,j in ca.items() if j.get('nanoda')])
