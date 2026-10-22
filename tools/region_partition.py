"""Pure stdlib exact graph-presence partition checker, extracted unchanged from S034."""
import itertools

def validate_partition(config, cells):
    variables = config['graph_variables']
    units = {int(k): v for k, v in config['graph_units'].items()}
    free = [v for v in variables if v not in units]
    bits = config['bits']
    assert len(cells) == 2**bits and bits <= len(free)
    assert [c['id'] for c in cells] == list(range(2**bits))
    assignments = list(itertools.product((False, True), repeat=bits))
    import math
    def weight(total, present):
        return sum(math.comb(total, m-present) for m in range(config['edge_low'], config['edge_high']+1)
                   if 0 <= m-present <= total)
    for cell, values in zip(cells, assignments, strict=True):
        expected = [v if b else -v for v, b in zip(free[:bits], values)]
        assert cell['assumptions'] == expected
        assert int(cell['weight']) == weight(len(free)-bits, sum(units.values())+sum(values))
    assert sum(int(c['weight']) for c in cells) == weight(len(free), sum(units.values()))
    return True
