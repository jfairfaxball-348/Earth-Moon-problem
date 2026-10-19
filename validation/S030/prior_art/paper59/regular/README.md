# Essential evidence for the regular endpoint theorem

Run from the supplement root:

    python3 regular/verify_rup.py

Use Python 3 with assertions enabled (do not use -O). No installation or
external input is needed. Expected status: PASS; q=2,3,4 respectively use
354,1338,1195 input clauses and 49,188,193 RUP additions. Each branch must
end in a checked empty clause. Typical elapsed time is approximately one
second on one CPU. The generated rup_verified.json is a report, not an input.

The manuscript proves that a counterexample to its abstract regular packing
theorem must have the stated zero-(5,6,6) profile. Its side classification
leaves only the three branches defined in branch_formulas.py after the
hand exclusion of T/T and U/U. These coverage arguments are distinct from
the finite proof replay and are not inferred from it.

encode.py regenerates a necessary relaxation using only the standard library.
branch_formulas.py adds the literal branch units. Each formula has 71,834
variables and 173,170 clauses. The packet gives indices of a subset of those
input clauses and literal RUP additions. Refuting that subset refutes the
full necessary formula. verify_rup.py checks every addition by direct unit
propagation, retaining all earlier clauses. No saved verdict or hash is
accepted as a proof. See SCHEMA.md and manuscript Sections 12–17 for details.

The fixed packet is 27,864 bytes with SHA-256:
b35f139e59467f20b771f090188fa5536d8342dcbc4446cf7945a74fb2fa64b3

Solvers were used only to discover these literal clauses. Their executables,
raw expanded proofs, trimming tools and logs are not needed to verify them.
All four files and this documentation are original CC0-1.0 code/data.
