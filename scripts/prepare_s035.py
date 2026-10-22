"""Prepare Windows campaign from independently accepted immutable S034 provenance."""
import argparse
import copy
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'scripts')]
from s035_windows import atomic_json
from s035_regions import sha, validate_partition
from import_s035 import rebase
AREA=ROOT/'artifacts/tmp/S035'

def prepared(workers=2, deadline=None):
    smoke=json.loads((AREA/'SMOKE.json').read_text())
    assert smoke['verdict']=='PASS' and smoke['chromatic_rows_verified']==smoke['chromatic_cnf_byte_matches']==271
    assert smoke['k9']['verified'] and smoke['solver_roundtrip']['fresh_proof_verified']
    controls=json.loads((AREA/'NATIVE_CONTROLS.json').read_text())
    scheduler=json.loads((AREA/'SCHEDULER_CONTROLS.json').read_text())
    audit=json.loads((AREA/'INPUT_AUDIT.json').read_text())
    imported=json.loads((AREA/'IMPORT_AUDIT.json').read_text())
    assert controls['exhaustive_n5_fixed_graphs']==1024 and controls['positive24']==controls['K33']=='PASS'
    assert scheduler['status']=='PASS' and scheduler['native_sha256']==controls['native_sha256']
    assert audit['status']=='PASS' and audit['independently_checked_native_clauses']==2579937
    assert imported['status']=='PASS' and len(imported['proofs'])==16 and imported['clauses']==93047
    for name,h in scheduler['source_sha256'].items(): assert sha(ROOT/name)==h,'Changed since scheduler controls: '+name
    cfg=rebase(json.loads((AREA/'imported-s034/CONFIG.json').read_text()))
    cfg.update(session='S035',root=str(ROOT),deadline=deadline,workers=workers,deadline_policy='OWNER_STOP_NO_FIXED_WALL_LIMIT' if deadline is None else 'PREREGISTERED_BENCHMARK',
        native=str(AREA/'native/bipsat_s032.exe'),cadical=str(ROOT/'artifacts/tmp/S004/cadical.exe'),checker=str(ROOT/'artifacts/tmp/S004/drat-trim-mingw.exe'),
        min_visit_seconds=600,max_visit_seconds=1800,rss_cap_kib=6*1024*1024,per_worker_private_bytes=2*1024**3,
        available_floor_kib=2*1024*1024,disk_reserve_bytes=10*1024**3,proof_cap_bytes=2*1024**3,
        aggregate_disk_bytes=40*1024**3,total_s035_disk_bytes=64*1024**3,temperature_cap_c=90,
        thermal_limitation='Windows core sensors unavailable; no thermal guarantee. Owner power/no-sleep confirmed.',
        concurrency_increase_validated=False,benchmark_seconds=120)
    cfg.pop('deadline_monotonic',None);cfg.pop('deadline_uk',None)
    cfg['native_sha256']=sha(cfg['native']);cfg['cadical_sha256']=sha(cfg['cadical']);cfg['checker_sha256']=sha(cfg['checker'])
    assert cfg['native_sha256']==controls['native_sha256']
    names=['tools/s035_windows.py','tools/s035_regions.py','tools/s035_engine.py','tools/s035_storage.py','scripts/s035_campaign.py','scripts/prepare_s035.py','scripts/benchmark_s035.py','scripts/import_s035.py','scripts/audit_s033_fast.py','tools/s032_subdivision.hpp']
    cfg['source_sha256']={name:sha(ROOT/name) for name in names}
    data=rebase(json.loads((AREA/'imported-s034/REGIONS.json').read_text()))
    assert validate_partition(cfg,data['cells'])
    data['import_provenance']=dict(original_config_sha256=sha(AREA/'imported-s034/CONFIG.json'),original_regions_sha256=sha(AREA/'imported-s034/REGIONS.json'),receipt=str(AREA/'IMPORT_AUDIT.json'))
    return cfg,data

def write_area(area,cfg,data):
    assert not area.exists(),'Never overwrite campaign'
    area.mkdir(parents=True)
    atomic_json(area/'CONFIG.json',cfg);atomic_json(area/'REGIONS.json',data)
    atomic_json(area/'CONTROLLER.json',dict(status='READY',deadline=cfg['deadline'],workers=cfg['workers'],verdict='UNKNOWN'))

if __name__=='__main__':
    cfg,data=prepared();write_area(AREA/'campaign',cfg,data)
