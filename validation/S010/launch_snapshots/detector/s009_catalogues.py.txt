"""Synchronise S009 source/claim ledgers without promoting pending construction verdicts."""
import json
from pathlib import Path
from s007_run import save

sources=json.loads(Path('catalogue/SOURCES.json').read_text(encoding='utf-8'))
notes={
 'SRC-0009':'S009 current v1 abstract/X1-X3/completion and alpha<=2 scope re-inspected; external Lean/LRAT not replayed.',
 'SRC-0012':'S009 direct Zenodo open unavailable; earlier statement access retained historically, no new proof access.',
 'SRC-0017':'S009 correct live earth-moon-biplanar API main/tree/date matches pinned5cb2ca9f7d4d6d195617c09f7348841636b646f6. Initial wrong shorter repository URL404 is not evidence about this source.',
 'SRC-0021':'S009 correct live repository API404 again; contents UNKNOWN.',
 'SRC-0027':'S009 Theorem1.3 local induction and Lemma3 good-colouring induction re-inspected; published blocking/counting methods attributed, entire Gallai/density proof not reconstructed.',
 'SRC-0029':'S009 primary v2 statements/local1.10 inspected; main proof/package not replayed, k47/352 and mad threshold restrictions intact.',
 'SRC-0030':'S009 direct open initially unavailable; later actual primary journal abstract returned by search. Earlier arXiv2024 preprint separately catalogued SRC0031; no2026 theorem priority inferred.'}
for s in sources:
    if s['id'] in notes:s['note']+=' '+notes[s['id']];s['accessed']='2026-10-14'
sources.extend([
 dict(id='SRC-0031',title='On graphs with chromatic number and maximum degree both equal to nine (arXiv v1)',
      authors='Rachel Galindo and Jessica McDonald',year=2024,publication_date='2024-08-22',
      url='https://arxiv.org/html/2408.12693v1',doi='10.48550/arXiv.2408.12693',
      access='STATEMENT_INSPECTED',accessed='2026-10-14',
      note='Earlier preprint of SRC0030. Primary Theorems3/5/6, Mozhan partition definitions and Lemmas9-11 statements inspected; proofs/referenced original lemmas not audited. Maximum-degree-nine restrictions do not cover actual12-critical biplanar graphs with unbounded high degree.'),
 dict(id='SRC-0032',title='Box-complex heights of the 9-chromatic biplanar record: only joins are topologically tight; K6 join I8 is biplanar (discussion lead)',
      authors='rStation platform handles opus_earthmoon, earth_moon_codex_two and lunar_structure; human authorship unverified',
      year=2026,publication_date='2026-10-11/12 comment dates in search excerpts; original post date unverified',
      url='https://rstation.ai/r/earth_moon/posts/86',access='METADATA_ONLY',accessed='2026-10-14',
      note='Search excerpts only; direct primary-page opens failed. At-most19/20-vertex claims are unverified discovery leads, not programme bounds. No primary theorem/proof/archives/certificates inspected, no outreach.'),
 dict(id='SRC-0033',title='A survey on vertex coloring problems',authors='Enrico Malaguti and Paolo Toth',year=2010,
      publication_date='2009-12-22 (first online)',url='https://doi.org/10.1111/j.1475-3995.2009.00696.x',
      doi='10.1111/j.1475-3995.2009.00696.x',access='STATEMENT_INSPECTED',accessed='2026-10-14',
      note='Primary survey Section2 same-colour contraction/different-colour branching explanation inspected; it attributes method to Mehrotra-Trick1996. Original algorithmic proof not audited. S009 equality quotient uses classical idea with explicit list/boundary proof, no planarity preservation/novelty claimed.')])
claims=json.loads(Path('catalogue/CLAIMS.json').read_text(encoding='utf-8'))
claims.extend([
 dict(id='CLM-0056',claim='For every selected family of t heavy K8 noncut cores in an actual12-critical biplanar graph, unweighted excess on the union of their high boundaries is at least4t, with arbitrary support overlap.',
      status='PROGRAMME_PROVED',sources=['SRC-0027','SRC-0014'],
      note='Complete all-order truncated-demand/degree-multiplicity proof in research/S009_GLOBAL_CHARGE.md;3331 finite charge checks corroborate only. Arithmetic equality model is not an actual critical biplanar witness. No maximum multiplicity, distinct high-excess representatives, universal colouring or novelty.'),
 dict(id='CLM-0057',claim='For every nonempty selected family of t heavy K8 endblocks in an actual12-critical biplanar graph, common high-boundary union size is at least ceil((8t+12)/6).',
      status='PROGRAMME_PROVED',sources=['SRC-0027','SRC-0014'],
      note='Distinct full eight-vertex low blocks contribute56t distinct edges on8t+a vertices. Complete Euler/subfamily/boundary proof in research/S009_GLOBAL_CHARGE.md. Stronger than noncut-only expansion, no colour/list conclusion.'),
 dict(id='CLM-0058',claim='For a fixed11-colouring outside all selected heavy-core boundaries, simultaneous extension exists iff some nonadjacent pair choice in each boundary induces independent equality classes whose quotient admits proper colouring from common-list intersections.',
      status='PROGRAMME_PROVED',sources=['SRC-0033'],
      note='Complete logical equivalence including cuts/overlaps/all edges/empty cases in research/S009_SIMULTANEOUS_COLOURS.md. Classical contraction idea attributed; no planar contraction or guaranteed feasible pair/list choices.1029 abstract list controls, not critical witnesses or universal theorem.'),
 dict(id='CLM-0059',claim='All completion K3,3 subgraph clauses in the registered S009 small full-layer tree model are necessary for every genuine planar completion.',
      status='PROGRAMME_PROVED',sources=['SRC-0009'],
      note='Bipartite Euler/six-set partition enumeration/orbit-minimum proof in research/S009_CONSTRUCTION.md;23 actual full pins/rotations and independent enumeration controls. Not all Kuratowski subdivisions, no SAT converse or verdict from partial CNFs.')])
assert len({s['id'] for s in sources})==len(sources)
assert len({c['id'] for c in claims})==len(claims)
save('catalogue/SOURCES.json',sources);save('catalogue/CLAIMS.json',claims)
text='# Source catalogue\n\nGrades describe actual access, not independent reproduction.\n'
for s in sources:
    text+=f"\n## {s['id']} — {s['access']}\n\n{s['title']} ({s['year']}). {s['authors']}.\n\n{s.get('url') or 'No primary URL inspected.'}\n\n{s.get('note','')}\n"
    text+=f"\nPublication date: {s.get('publication_date','unspecified')}; accessed: {s.get('accessed','unspecified')}.\n"
Path('catalogue/SOURCES.md').write_text(text,encoding='utf-8',newline='\n')
text='# Claim catalogue\n\nStatus records evidence; no programme claim resolves EMP.\n'
for c in claims:
    text+=f"\n## {c['id']} — {c['status']}\n\n{c['claim']}\n\nSources: {', '.join(c['sources']) or 'None; programme proof/computation.'}.\n\n{c.get('note','')}\n"
Path('catalogue/CLAIMS.md').write_text(text,encoding='utf-8',newline='\n')
print('PASS paired catalogues; no pending construction promotion')
