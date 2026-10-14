"""Freeze public positive inputs; recheck full pins/rotations under supervision."""
import datetime,json,sys
from pathlib import Path
from s005_replay import sha
from s005_search import run_logged
from s007_run import save
ROOT=Path('validation/S009');TMP=Path('artifacts/tmp/S009/public_controls')

def capture():
    from biplanar_cnf import read_edges
    old=json.loads((ROOT/'heavy_controls.json').read_text());rows=[]
    for r in old:
        tag=r['name']
        ef=Path('artifacts/tmp/S009/replay')/(tag+'.edges') if tag[-2:].isdigit() else Path('validation/S003/splits')/(tag[len('control-'):]+'.edges')
        edges=set(read_edges(str(ef)));layers=[set(map(tuple,es)) for es in r['pin']['completion_edges']]
        assert edges<=layers[0]|layers[1]
        a=edges&layers[0];b=edges-a
        rows.append(dict(tag=tag,n=r['n'],edges=sorted(edges),split=dict(n=r['n'],E1=sorted(a),E2=sorted(b)),
            original_completed_layers=r['pin']['completion_edges'],input_edge_sha256=sha(ef)))
    save(ROOT/'pinned_positive_inputs.json',rows)
    save(ROOT/'positive_input_capture.json',dict(grade='AFTER_ORIGINAL_CONTROL_LAUNCH_BEFORE_PUBLIC_REPEAT',
        source='validation/S009/heavy_controls.json',source_sha256=sha(ROOT/'heavy_controls.json'),
        payload_sha256=sha(ROOT/'pinned_positive_inputs.json'),controls=len(rows)))

def worker():
    import s007_static_controls
    from s009_heavy_cover import HeavyCover
    from check_layers import main as check_split
    s007_static_controls.StrongCover=HeavyCover;TMP.mkdir(parents=True,exist_ok=True)
    rows=[]
    for r in json.loads((ROOT/'pinned_positive_inputs.json').read_text()):
        ef=TMP/(r['tag']+'.edges');sf=TMP/(r['tag']+'.split.json')
        ef.write_text(''.join(f'{a} {b}\n' for a,b in r['edges']),newline='\n');save(sf,r['split'])
        check_split(str(ef),str(sf))
        pin=s007_static_controls.static_control(str(ef),str(sf))
        rows.append(dict(tag=r['tag'],edge_sha256=sha(ef),split_sha256=sha(sf),pin=pin))
        save(ROOT/'public_control_repeat.json',rows)
    assert len(rows)==23;print('PASS23 self-contained public controls: input union/rotations/full primary pins',flush=True)

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='worker':worker();raise SystemExit
    assert not (ROOT/'public_control_observed_launch.json').exists();capture()
    files=['tools/s009_public_controls.py','tools/s009_heavy_cover.py','tools/s007_static_controls.py',
           'tools/s005_search.py','validation/S009/pinned_positive_inputs.json','campaigns/CAM-0010.md']
    cmd=[sys.executable,'tools/s009_public_controls.py','worker']
    snap=ROOT/'launch_snapshots/public_controls';snap.mkdir(parents=True,exist_ok=True)
    for f in files:(snap/(Path(f).name+'.txt')).write_bytes(Path(f).read_bytes())
    save(ROOT/'public_control_observed_launch.json',dict(command=cmd,as_of_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        sha256={f:sha(f) for f in files},grade='OBSERVED_BEFORE_LAUNCH'))
    r=run_logged(cmd,920,ROOT/'public_control_repeat.log');save(ROOT/'public_control_command.json',r)
    print(r,flush=True);assert r['returncode']==0
