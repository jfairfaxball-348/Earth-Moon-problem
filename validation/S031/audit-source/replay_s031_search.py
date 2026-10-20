"""Replay S031 saved assignments, chronological formula and semantic cuts.

Does not run search or infer a stratum decision from a capped execution.
"""
import collections
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from s030_op1b import encode
from s031_check import cut, model


def read(p):
    return p.read_bytes() if p.exists() else gzip.decompress(p.with_suffix(p.suffix+'.gz').read_bytes())


def audit(base):
    started = time.monotonic()
    load = lambda name: json.loads(read(base/name))
    result = load('RESULT.json')
    checkpoint = load('CHECKPOINT.json')
    cuts = load('CUTS.json')
    assert checkpoint['cuts'] == cuts and len(cuts) == result['cuts'] == 1809
    assert result['status'] == 'WALL_CAPPED' and result['verdict'] == 'UNKNOWN'
    assert not result['witness_candidate'] and not result['whole_stratum_certified']
    assert hashlib.sha256(read(base/'final.cnf')).hexdigest() == result['final_cnf_sha256']
    assert hashlib.sha256(read(base/'CUTS.json')).hexdigest() == result['cuts_sha256']
    formula, g, layers = encode(28, 11, 155, 156, anchor=True, sorted_anchor=True)
    variables = load('VARIABLES.json')
    assert variables == {'g': [[*e,x] for e,x in g.items()],
                         'layers': [[[*e,x] for e,x in ls.items()] for ls in layers]}
    base_count = len(formula.clauses)
    cnf = read(base/'final.cnf').decode().splitlines()
    header = next(l for l in cnf if l.startswith('p ')).split()
    clauses = [list(map(int,l.split()[:-1])) for l in cnf if l and l[0] not in 'cp']
    assert int(header[2]) == formula.nv and int(header[3]) == len(clauses)
    assert clauses == formula.clauses + [c['clause'] for c in cuts]
    kinds = collections.Counter()
    for c in cuts:
        cut(c,g,layers)
        kinds[c['kind']] += 1
    seed = cuts[:result['seed_cuts']]
    assert len(seed) == 1114
    expected_seed = []
    seen = set()
    for segment in ('sorted','pilot'):
        for c in json.loads((ROOT/f'validation/S030/{segment}/CUTS.json').read_text()):
            key = tuple(sorted(c['clause']))
            if key not in seen:
                seen.add(key); expected_seed.append(c)
    assert seed == expected_seed
    generated = cuts[len(seed):]
    journal = [json.loads(l)['cut'] for l in read(base/'CUT_JOURNAL.jsonl').decode().splitlines()]
    assert journal == generated
    for c in seed: formula.append(c['clause'])
    models = sorted((base/'models').glob('*.json.gz'))
    assert len(models) == result['models'] == 46
    per_model=[]
    for i,path in enumerate(models,1):
        assert path.name == f'{i:07d}.json.gz'
        data=json.loads(gzip.decompress(path.read_bytes()))
        assert data['n'] == 28 and data['clauses_before'] == len(formula.clauses)
        positive=set(data['positive_model'])
        graph, parts=model(positive,g,layers,formula)
        assert parts == [set(map(tuple,data[k])) for k in ('E1','E2')]
        added=[c for c in generated if c['model_number'] == i]
        assert added
        for c in added:
            assert all(-x in positive for x in c['clause'])
            if c['kind']=='Kuratowski':
                assert set(map(tuple,c['edges'])) <= parts[c['layer']]
            formula.append(c['clause'])
        assert sum(c['kind']=='Kuratowski' for c in added) == 2
        per_model.append({'model':i,'edges':graph.number_of_edges(),'cuts':len(added),
                          'both_layers_nonplanar_by_checked_subdivisions':True})
    assert formula.clauses == clauses
    return {'status':'PASS','models_checked':len(models),'cuts_checked':len(cuts),
            'seed_cuts':len(seed),'new_cuts':len(generated),'cut_types':dict(kinds),
            'base_clauses':base_count,'final_clauses':len(clauses),'variables':formula.nv,
            'chronological_assignment_checks':True,'final_formula_regenerated':True,
            'each_model_has_two_checked_nonplanar_layers':True,
            'whole_stratum_certified':False,'verdict':'UNKNOWN','per_model':per_model,
            'seconds':round(time.monotonic()-started,3)}


if __name__ == '__main__':
    base=ROOT/(sys.argv[1] if len(sys.argv)>1 else 'artifacts/tmp/S031/search')
    result=audit(base)
    output=ROOT/'artifacts/tmp/S031/SEARCH_REPLAY.json'
    output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k!='per_model'},indent=2))
