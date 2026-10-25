"""Write the S046 preregistration before any diagnostic or pilot computation."""
import hashlib
import json
from pathlib import Path
import random
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'validation/S046/REGISTRATION.json'

TOTAL = 642381
STRATA = [('early', 0, 214127), ('middle', 214127, 428254), ('late', 428254, TOTAL)]
SEED = 46046
ORDERS = [24, 28, 32, 40, 50]
ARMS = ['B', 'C', 'CS']


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main():
    assert not OUT.exists(), 'registration is write-once'
    audit = json.loads((ROOT / 'validation/S045/final/AUDIT.json').read_text())
    assert audit['candidate_records'] == TOTAL
    rng = random.Random(SEED)
    sample = {name: sorted(rng.sample(range(lo, hi), 100)) for name, lo, hi in STRATA}
    now = time.time()
    data = dict(
        session='S046', directive='D078', status='REGISTERED_BEFORE_EXPERIMENT',
        executor='Claude Code desktop app, model claude-opus-5-5, owner Windows laptop',
        entry=dict(main='5f56fdf14b88eef9b77f549679c35a1e59a5b106',
                   tree='150651489c2f1afae044f9d82461cf23c7cf0d79',
                   parent='a55d0d00ce5eb620df941ee19650e3a2d804639e',
                   hosted_run=40176540308, hosted_conclusion='success'),
        registered_epoch=now,
        registered_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now)),
        experimental_deadline_epoch=now + 4 * 3600,
        budget=dict(total_cpu_seconds=1800, total_wall_seconds=3600,
                    blocks=dict(E1=dict(cpu=360, wall=480), E2=dict(cpu=1050, wall=1150),
                                E3=dict(cpu=180, wall=240), E4=dict(cpu=200, wall=260)),
                    ledger='artifacts/tmp/S046/BUDGET.jsonl',
                    verification_costs_separate=True),
        resources=dict(private_memory_hard_bytes=3 * 2**30, available_floor_bytes=int(1.5 * 2**30),
                       disk_reserve_bytes=10 * 2**30, heavy_generators=1, oracle='serial'),
        e1=dict(archive_index='validation/S045/final/ARCHIVE_INDEX.json',
                archive_index_sha256=sha('validation/S045/final/ARCHIVE_INDEX.json'),
                expected_records=TOTAL, strata=STRATA, seed=SEED, per_stratum=100,
                sample_indices=sample,
                caps=dict(sat8_seconds=2, clique_seconds=2, drat_solve_seconds=20, drat_check_seconds=30),
                classification=dict(mainly_easy='>=50% of all records have empty 9-core',
                                    mainly_redundant='>=50% of sample in non-singleton isomorphism classes',
                                    plausible_cores='>=50% of sample nonempty 9-core and checked non-8-colourable',
                                    otherwise='UNDETERMINED_BY_BOUNDED_DIAGNOSIS')),
        e2=dict(orders=ORDERS, arms=ARMS, k=9, solve_seconds=60, startup_ceiling=120,
                feedback='partition', positive_phases=True, oracle='pysat glucose4',
                execution='orders ascending; arms B, C, CS', clause_transfer=False,
                arm_definitions=dict(
                    B='S045 domain at order n: all pairs optional, layer disjointness',
                    C='B + union degree >= 9 at every vertex (sequential at-least counter)',
                    CS='C + union vars, lex-leader row_i >=lex row_j (cols != i,j) all i<j, first union pair in layer 1'),
                unrun=dict(variable_active_core_50='NOT_RUN_BUDGET',
                           sat_modulo_symmetries='BLOCKED_SINGLE_EXTERNAL_PROPAGATOR',
                           kostochka_yancey_and_2connectivity='NOT_ENCODED_NECESSARY_ONLY')),
        e3=dict(per_arm=30, seed_base=SEED, sat8_seconds=0.5, per_arm_wall_cap=12,
                drat_solve_seconds=5, drat_check_seconds=15,
                targeting_criterion=dict(
                    T1='>=20 validated candidates and >=20 analysed',
                    T2='p9>=0.25 and Wilson95 lower(p9 arm) > Wilson95 upper(p9 baseline, same n)',
                    p9='analysed candidates with drat-trim-checked non-8-colourability / analysed',
                    ranking='(validated candidates per solve second) * p9; ties to smaller n')),
        e4=dict(condition='some C/CS arm passes T',
                acceptance='>=120 s native solve, >=50 new independently checked records, below caps, restart from byte-hash-verified sealed checkpoint, no full prefix re-audit',
                controls=['corrupt checkpoint', 'truncated checkpoint', 'byte hashes',
                          'stop/deadline in preparation, loading, solving, audit', 'memory recycling',
                          'no-progress stop', 'native UNSAT concurrent with recycling',
                          'first cause and PID/create/exe identity']),
        decision=dict(SELECT='T passes and E4 acceptance passes', otherwise='PIVOT_OR_INCONCLUSIVE'),
        plan_sha256=sha('sessions/S046/PLAN.md'),
        long_run_started=False, automation_created=False, s047_executed=False)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open('x', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(data, indent=1) + '\n')
    print('registered', data['registered_utc'], hashlib.sha256(OUT.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
