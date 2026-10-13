#!/usr/bin/env python3
"""Proof export adapter; every resulting proof MUST be independently checked.

Usage: export_pysat_drat.py CNF PROOF.drat
Windows C-runtime flush is needed before reading the proof FILE through
Python's descriptor. Do not strip binary bytes before decoding DRAT.
"""
import ctypes
import os
import sys
from pathlib import Path

from pysat.formula import CNF
from pysat.solvers import Cadical153, Solver


def main(cnf, proof):
    with Cadical153(bootstrap_with=CNF(from_file=cnf).clauses,with_proof=True) as s:
        verdict=s.solve()
        print('solver status',verdict,flush=True)
        assert verdict is False, 'no UNSAT proof to export'
        if os.name == 'nt':
            crt=ctypes.CDLL('ucrtbase')
            crt.fflush.argtypes=[ctypes.c_void_p]
            crt.fflush.restype=ctypes.c_int
            print('fflush(NULL)',crt.fflush(None),flush=True)
        s.prfile.seek(0)
        raw=s.prfile.read()
        lines=Solver._proof_bin2text(bytearray(raw))
        Path(proof).write_text('\n'.join(lines)+'\n',newline='\n')
        print('raw bytes',len(raw),'lines',len(lines),'tail',lines[-2:],flush=True)


if __name__ == '__main__':
    main(*sys.argv[1:3])
