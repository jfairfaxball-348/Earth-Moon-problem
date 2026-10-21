"""Exercise real-native bounded completion, STOP, SIGTERM and orphan recovery."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/"artifacts/tmp/S033"
cmd=[sys.executable,str(ROOT/"scripts/s033_phone.py")]
state=AREA/"PHONE.json"
rows=[]
def wait_started(p):
    deadline=time.monotonic()+5
    while time.monotonic()<deadline:
        if state.exists():
            r=json.loads(state.read_text())
            if r.get("controller_pid")==p.pid and r["status"]=="RUNNING":return r
        assert p.poll() is None
        time.sleep(.02)
    raise AssertionError("Controller failed to start")
for mode in ("bounded","stop","signal","kill_recover"):
    with (AREA/(mode+"-controller.log")).open("w") as log:
        p=subprocess.Popen(cmd+["run","--input",str(AREA/"controls-v2/K9.inst"),"--seconds","5"],stdout=log,stderr=subprocess.STDOUT)
        started=wait_started(p)
        if mode=="bounded":
            duplicate=subprocess.run(cmd+["run","--input",str(AREA/"controls-v2/K9.inst"),"--seconds","1"],capture_output=True,text=True)
            assert duplicate.returncode!=0 and "active" in duplicate.stderr
            p.wait(timeout=10)
        elif mode=="stop":
            subprocess.run(cmd+["stop"],check=True);p.wait(timeout=5)
        elif mode=="signal":
            p.send_signal(signal.SIGTERM);p.wait(timeout=5)
        else:
            p.kill();p.wait(timeout=5)
            subprocess.run(cmd+["recover"],check=True)
        r=json.loads(state.read_text());assert r["verdict"]=="UNKNOWN"
        if mode=="bounded":assert r["status"]=="FINISHED_UNKNOWN"
        elif mode=="kill_recover":assert r["status"]=="RECOVERED_UNKNOWN"
        else:assert r["status"]=="OWNER_STOP"
        worker=Path("/proc")/str(started["worker_pid"])/"stat"
        if worker.exists():
            assert worker.read_text().rsplit(")",1)[1].split()[0]=="Z", "Live orphan remains"
        rows.append({"mode":mode,"status":r["status"],"record":r})
# Exercise the separate standalone-proof supervisor with a real native worker.
sys.path.insert(0,str(ROOT/"tools"))
from s026_supervision import linux_tree
code="import sys;from pathlib import Path;sys.path[:0]=[str(Path.cwd()/'scripts'),str(Path.cwd()/'tools')];from s033_coverage_core import supervise;supervise(sys.argv[1:],Path('artifacts/tmp/S033/coverage-signal-worker.log'),10)"
with (AREA/"coverage-signal-controller.log").open("w") as log:
    p=subprocess.Popen([sys.executable,"-c",code,str(AREA/"native/bipsat_s033"),str(AREA/"controls-v2/K9.inst"),"--timeout","5"],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    deadline=time.monotonic()+3;children=set()
    while time.monotonic()<deadline:
        children=linux_tree(p.pid)[0]-{p.pid}
        if children:break
        assert p.poll() is None;time.sleep(.02)
    assert children
    p.send_signal(signal.SIGTERM);p.wait(timeout=5)
    for pid in children:
        stat=Path(f"/proc/{pid}/stat")
        if stat.exists():assert stat.read_text().rsplit(")",1)[1].split()[0]=="Z"
subprocess.run(cmd+["status"],check=True,stdout=subprocess.DEVNULL)
out=ROOT/"validation/S033/LIFECYCLE.json"
out.write_text(json.dumps({"status":"PASS","rows":rows,"coverage_SIGTERM_cleanup":True},indent=2)+"\n")
print("PASS bounded native run, STOP, SIGTERM, unexpected kill/recovery and read-only status")
