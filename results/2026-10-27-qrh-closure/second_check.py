import subprocess, re, sys, csv
clone='/home/checker/math'; out=sys.argv[1]
A='adc7f1241b42e322a6451854ab7e4b4c146bf78a'; F='fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb'
ch=subprocess.run(['git','-C',clone,'diff','--name-only',A,F,'--','lean'],capture_output=True,text=True).stdout.split()
chmods={p[len('lean/'):-len('.lean')].replace('/','.') for p in ch if p.endswith('.lean')}
clos=[r['name'] for r in csv.DictReader(open(out+'/qrh-closure.tsv',encoding='utf-8'),delimiter='\t') if r['kind']=='local module']
hits=[]
for m in clos:
    t=subprocess.run(['git','-C',clone,'show',F+':lean/'+m.replace('.','/')+'.lean'],capture_output=True).stdout.decode('utf-8','replace')
    for i,l in enumerate(t.split('\n'),1):
        if re.match(r'^\s*(?:(?:public|private|meta)\s+)*import\b',l) and set(l.split()) & chmods: hits.append((m,i,l.strip()))
inclos=sorted(chmods & set(clos))
with open(out+'/second-check.txt','x',encoding='utf-8',newline='\n') as o:
    print('# Second method (2026-10-27): every lean/ file changed between adc7f12 and fd4aeeb (git diff --name-only), checked against the closure in qrh-closure.tsv', file=o)
    print('# by scanning every line (not only the header) of each closure file at fd4aeeb for an import line naming a changed module. Command: python3 -I <scratch script> results/2026-10-27-qrh-closure (as checker in WSL)', file=o)
    print(f'files changed under lean/: {len(ch)}; of them .lean modules: {len(chmods)}; other files: {sorted(p for p in ch if not p.endswith(".lean"))[:20]}', file=o)
    print(f'changed modules that are in the closure: {inclos}', file=o)
    print(f'import lines anywhere in closure files that name a changed module: {len(hits)} {hits[:10]}', file=o)
print(open(out+'/second-check.txt',encoding='utf-8').read())
