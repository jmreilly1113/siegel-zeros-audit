"""Extended replay, Phase 1: peak-memory sampler and export capture for ONE comparator run (outside the sandbox; read-only
on the unit). Run as root, in the background, just before 67_corpus_run.sh is called with the same config path.

Usage: python3 -I 111_memsample.py <config path> <out json> [<export copy path>]

Finds the sandbox's transient unit (systemd-run --user, app.slice/run-u*.service) by its main process: a process of uid
checker whose cmdline contains the config path and whose unified-cgroup path contains /run-u. No unit property is set
or changed. Every 0.5 s it reads cgroup.procs of that unit's unified cgroup and, for each process, VmRSS and VmHWM from
/proc/<pid>/status. Records:
  peak_rss_sum_kb   max over samples of the sum of VmRSS of all processes in the unit (sampled; lower bound of the true peak)
  peak_hwm_kb       max VmHWM of any single process (kernel high-water mark; exact for that process up to its last sample)
  peak_hwm_proc     that process's name and the first 120 characters of its cmdline
Why not memory.peak / MemoryPeak / cgroup v1 max_usage: kernel 5.15 has no memory.peak, systemd 255 has no MemoryPeak,
and in this hybrid setup the unit's v1 memory cgroup is the whole user@1000.service, shared and holding page cache.
/usr/bin/time outside the wrapper would time the systemd-run client, not the unit (the unit is not its child).
Export capture: when a process in the unit has nanoda_bin in its cmdline, its last argument is the nanoda config
Comparator wrote; the sampler opens the config and the export_file_path it names (an open descriptor survives the
unlink after nanoda exits), then hashes the export and, if <export copy path> is given, copies both files.
The sampler stops when the unit's cgroup disappears, or after 600 s if the unit never appears.
"""
import hashlib, json, os, shutil, sys, threading, time

cfg, out = sys.argv[1], sys.argv[2]
copy_to = sys.argv[3] if len(sys.argv) > 3 else None
CHECKER = 1000
res = {'method': 'sampled unified cgroup of the transient unit, 0.5 s; VmRSS sum and per-process VmHWM (111_memsample.py)',
       'config': cfg, 'unit_cgroup': None, 'samples': 0, 'peak_rss_sum_kb': None, 'peak_hwm_kb': None,
       'peak_hwm_proc': None, 'export': None, 'first_seen': None, 'last_seen': None}


def status(pid):
    d = {}
    try:
        for l in open(f'/proc/{pid}/status'):
            k, _, v = l.partition(':')
            d[k] = v.strip()
    except OSError:
        return None
    return d


def cmdline(pid):
    try:
        return open(f'/proc/{pid}/cmdline', 'rb').read().split(b'\0')
    except OSError:
        return []


def ucg(pid):
    try:
        for l in open(f'/proc/{pid}/cgroup'):
            if l.startswith('0::'):
                return l[3:].strip()
    except OSError:
        return None


t0 = time.time()
unit = None
while unit is None and time.time() - t0 < 600:
    for p in os.listdir('/proc'):
        if not p.isdigit():
            continue
        st = status(p)
        if not st or int(st.get('Uid', '0').split()[0]) != CHECKER:
            continue
        cl = b' '.join(cmdline(p)).decode('utf-8', 'replace')
        g = ucg(p)
        if cfg in cl and g and '/run-u' in g and g.endswith('.service'):
            unit = g
            break
    time.sleep(0.2)
if unit is None:
    res['error'] = 'unit not found within 600 s'
    json.dump(res, open(out, 'w'), indent=1)
    sys.exit(0)
res['unit_cgroup'] = unit
res['first_seen'] = time.strftime('%F %T')
D = '/sys/fs/cgroup/unified' + unit
peak_sum, peak_hwm, peak_proc = 0, 0, None
exp_threads = []


def capture(pid):
    args = cmdline(pid)
    conf = args[-2].decode() if args and args[-1] == b'' else (args[-1].decode() if args else '')
    info = {'nanoda_pid': int(pid), 'nanoda_config': conf}
    try:
        fc = open(conf, 'rb')
        cj = json.loads(fc.read().decode())
        fe = open(cj['export_file_path'], 'rb')
    except (OSError, ValueError, KeyError) as e:
        info['error'] = f'could not open config/export: {e}'
        res['export'] = info
        return
    info['export_file_path'] = cj['export_file_path']
    info['nanoda_config_json'] = cj

    def work():
        h = hashlib.sha256(); n = 0
        dst = open(copy_to, 'wb') if copy_to else None
        while True:
            b = fe.read(1 << 22)
            if not b:
                break
            h.update(b); n += len(b)
            if dst:
                dst.write(b)
        if dst:
            dst.close()
            json.dump(cj, open(copy_to + '.nanoda-config.json', 'w'), indent=1)
        info['export_sha256'] = h.hexdigest(); info['export_bytes'] = n
        info['copied_to'] = copy_to
    th = threading.Thread(target=work); th.start(); exp_threads.append(th)
    res['export'] = info


while os.path.isdir(D):
    try:
        pids = open(D + '/cgroup.procs').read().split()
    except OSError:
        break
    s = 0
    for p in pids:
        st = status(p)
        if not st:
            continue
        rss = int(st.get('VmRSS', '0 kB').split()[0]); hwm = int(st.get('VmHWM', '0 kB').split()[0])
        s += rss
        if hwm > peak_hwm:
            peak_hwm = hwm
            peak_proc = st.get('Name', '?') + ' | ' + b' '.join(cmdline(p)).decode('utf-8', 'replace')[:120]
        if res['export'] is None and any(a.endswith(b'nanoda_bin') for a in cmdline(p)):
            capture(p)
    peak_sum = max(peak_sum, s)
    res['samples'] += 1
    time.sleep(0.5)
for th in exp_threads:
    th.join()
res['last_seen'] = time.strftime('%F %T')
res['peak_rss_sum_kb'] = peak_sum; res['peak_hwm_kb'] = peak_hwm; res['peak_hwm_proc'] = peak_proc
json.dump(res, open(out, 'w'), indent=1)
