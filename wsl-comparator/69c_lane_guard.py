#!/usr/bin/env python3
"""Extended replay lane guard 69c (2026-10-23; replaces 69b for 114d). Run as root.

Why: 69/69b stop EVERY checker job when memory runs low, so one heavy job kills the others' work, and 119c must then
guess afterwards which config was to blame. 69c acts on one job at a time, by lane, using each job's systemd unit
cgroup (v2 cgroup.freeze / cgroup.kill):
  lanes (lowest priority first): build (main-lane prebuild) < run (main-lane comparator run / query) < slow (slow lane)
  A = MemAvailable + SwapFree (MB), polled every POLL s
  A < SOFT  and a build runs beside another job -> freeze the build (PAUSE); it keeps its memory but stops growing
  build frozen and (A > RESUME or it is the only job) -> thaw it (RESUME)
  A < HARD  and >= 2 jobs -> kill the lowest-priority job only (PREEMPT) and write <out>/preempt/<config>.<lane>;
                             114d retries that job (a build at fewer threads; a run later). Not a verdict.
  A < HARD  and 1 job (or a disk-limit breach) -> the 69/69b full stop, unchanged: "LIMIT: ..." line in guard.log,
                             pkill of checker's lake/lean/comparator, GUARD_STOPPED marker, exit 1 (119c handles it).
Log lines: "guard start", "LIMIT:", "stopped", "drop_caches" as 69b; plus "PAUSE", "RESUME", "PREEMPT" (no "LIMIT:").
Lane of a unit: from its root command (the `timeout ...` process): 'lake build' -> build; otherwise the config name
from the command ('lake env comparator <cfg>', nanoda direct '<N>.f67473b-config.json', 'lake env lean <N>-axioms...')
-> slow if it is listed in <out>/active-slow.txt (up to 2 lines), else run. Queries ('lake env lean') are never preempted,
and the top-priority job present is preempted only if another job of the same lane is running (two slow jobs).
Usage: 69c_lane_guard.py <out dir> [DISK_GB 85] [SOFT 4500] [HARD 2000] [RESUME 8000]
Test hooks: GUARD_LOG, GUARD_MARK, GUARD_MEMINFO, GUARD_POLL, GUARD_DRYRUN=1 (no pkill / drop_caches in the full stop),
GUARD_TAG (only units whose root command contains this string are touched), GUARD_MAXLOOPS.
"""
import os, sys, time, glob, re, signal, subprocess, shutil

OUT = sys.argv[1]
DISK = int(sys.argv[2]) if len(sys.argv) > 2 else 85
SOFT = int(sys.argv[3]) if len(sys.argv) > 3 else 4500
HARD = int(sys.argv[4]) if len(sys.argv) > 4 else 2000
RESUME = int(sys.argv[5]) if len(sys.argv) > 5 else 8000
LOG = os.environ.get('GUARD_LOG', '/home/checker/corpus/guard.log')
MARK = os.environ.get('GUARD_MARK', '/home/checker/corpus/GUARD_STOPPED')
MI = os.environ.get('GUARD_MEMINFO', '/proc/meminfo')
POLL = float(os.environ.get('GUARD_POLL', '5'))
DRY = os.environ.get('GUARD_DRYRUN', '0') == '1'
TAG = os.environ.get('GUARD_TAG', '')
MAXLOOPS = int(os.environ.get('GUARD_MAXLOOPS', '0'))
APP = '/sys/fs/cgroup/unified/user.slice/user-1000.slice/user@1000.service/app.slice'
PRI = {'build': 0, 'run': 1, 'slow': 2}
CHECKER = int(subprocess.run(['id', '-u', 'checker'], capture_output=True, text=True).stdout.strip() or 1000)

def now(): return time.strftime('%Y-%m-%d %H:%M:%S')
def log(s):
    with open(LOG, 'a') as f: f.write(f'{now()} {s}\n')
def rd(p, d=''):
    try:
        with open(p) as f: return f.read()
    except OSError: return d
def wr(p, s):
    try:
        with open(p, 'w') as f: f.write(s)
        return True
    except OSError: return False

def mem():
    t = rd(MI); g = lambda k: int((re.search(rf'^{k}:\s+(\d+)', t, re.M) or [0, 0])[1]) // 1024
    return g('MemAvailable'), g('SwapFree')

def disk_used_gb():
    return shutil.disk_usage('/').used // (1024 ** 3) if not os.environ.get('GUARD_DISK') else int(os.environ['GUARD_DISK'])

def name_of(cmd):
    m = re.search(r'lake env comparator (\S+)', cmd)
    if m: return os.path.basename(m.group(1)).split('.')[0].split('-')[0]
    m = re.search(r'/([A-Za-z0-9_]+)\.f67473b-config\.json', cmd)
    if m: return m.group(1)
    m = re.search(r'lake env lean \S*/([A-Za-z0-9_]+)-(axioms|audit)', cmd)
    if m: return m.group(1)
    return ''

def units():
    """[(lane, config, unit dir, pids, is_query)] for checker units with a `timeout` root process."""
    slow = set(rd(f'{OUT}/active-slow.txt').split()); bld = rd(f'{OUT}/active-build.txt').strip()
    res = []
    for d in glob.glob(f'{APP}/run-*.service'):
        pids = [int(x) for x in rd(f'{d}/cgroup.procs').split()]
        root = ''
        for p in pids:
            try:
                if os.stat(f'/proc/{p}').st_uid != CHECKER: continue
                a = rd(f'/proc/{p}/cmdline').split('\0')
            except OSError: continue
            if a and os.path.basename(a[0]) == 'timeout': root = ' '.join(a); break
        if not root or (TAG and TAG not in root): continue
        if 'lake build' in root: res.append(('build', bld, d, pids, False)); continue
        n = name_of(root)
        res.append(('slow' if n and n in slow else 'run', n, d, pids, 'lake env lean' in root))
    return res

def freeze(d, v): return wr(f'{d}/cgroup.freeze', '1' if v else '0')
def kill(d, pids):
    if not wr(f'{d}/cgroup.kill', '1'):
        for p in pids:
            try: os.kill(p, signal.SIGKILL)
            except OSError: pass

def full_stop(u, a, s, why):
    log(f'LIMIT: disk {u}G, MemAvailable {a}MB, SwapFree {s}MB; {why}; stopping checker build processes')
    if DRY: log('(dry run: nothing killed)')
    else:
        subprocess.run(['pkill', '-TERM', '-u', 'checker', '-f', 'comparator|lake|lean']); time.sleep(20)
        subprocess.run(['pkill', '-KILL', '-u', 'checker', '-f', 'comparator|lake|lean']); subprocess.run(['sync'])
    log('stopped'); open(MARK, 'a').close(); sys.exit(1)

os.makedirs(f'{OUT}/preempt', exist_ok=True)
log(f'guard start: disk limit {DISK}G, 69c lane guard: MemAvailable+SwapFree soft {SOFT} / hard {HARD} / resume {RESUME} MB, poll {POLL:g} s')
frozen = {}   # unit dir -> (config, since)
n = 0
while True:
    n += 1
    a, s = mem(); A = a + s; u = disk_used_gb(); js = units()
    live = {j[2] for j in js}
    for d in list(frozen):                       # a frozen unit that ended
        if d not in live: del frozen[d]
    if u > DISK: full_stop(u, a, s, 'disk limit')
    builds = [j for j in js if j[0] == 'build']
    others = [j for j in js if j[0] != 'build']
    if A < HARD:
        # victims: not a short query (killing one frees little), and never the top-priority job present
        top = max(PRI[j[0]] for j in js) if js else 0
        cand = [j for j in js if not j[4] and (PRI[j[0]] < top or sum(1 for k in js if PRI[k[0]] == top) > 1)]
        if len(js) >= 2 and cand:
            v = min(cand, key=lambda j: (PRI[j[0]], -len(j[3])))
            kill(v[2], v[3]); frozen.pop(v[2], None)
            open(f'{OUT}/preempt/{v[1] or "unknown"}.{v[0]}', 'a').write(f'{now()} A={A}MB\n')
            log(f'PREEMPT {v[0]} {v[1]} (MemAvailable {a}MB, SwapFree {s}MB; {len(js)} jobs); unit {os.path.basename(v[2])} killed')
            time.sleep(10); continue
        if len(js) == 1: full_stop(u, a, s, 'one job left')
        # >= 2 jobs but no candidate (only queries beside the top job): wait for the queries to end
    for (lane, cfg, d, pids, _) in builds:
        if d in frozen:
            if A > RESUME or not others:
                freeze(d, False); log(f'RESUME build {cfg} after {int(time.time() - frozen[d][1])} s (MemAvailable {a}MB, SwapFree {s}MB)'); del frozen[d]
        elif A < SOFT and others:
            if freeze(d, True): frozen[d] = (cfg, time.time()); log(f'PAUSE build {cfg} (MemAvailable {a}MB, SwapFree {s}MB; beside {",".join(o[1] for o in others)})')
    if n % max(1, int(60 / POLL)) == 0:
        if not DRY: subprocess.run(['sync']); wr('/proc/sys/vm/drop_caches', '1')
        log(f'drop_caches; disk {u}G MemAvailable {a}MB SwapFree {s}MB; jobs {" ".join(j[0] + ":" + j[1] for j in js) or "-"}; frozen {len(frozen)}')
    if MAXLOOPS and n >= MAXLOOPS: break
    time.sleep(POLL)
