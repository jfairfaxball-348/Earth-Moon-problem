# S047 prior art — contradiction-route feasibility

Searches run 29 October 2026 from the cloud container (WebSearch/WebFetch).
Access grades are honest; search excerpts are not proof inspection.

| Topic | Finding | Source / grade |
|---|---|---|
| Earth-Moon status | Bounds 9 <= chi_2 <= 12 unchanged in all found sources (Epoch AI open-problem page, Open Problem Garden, 2018 survey). No reported chi >= 10 biplanar graph. | catalogue SRC-0002/0003 unchanged; search excerpts only |
| alpha <= 2 route | Szeider (arXiv 2609.28102, 23 Sep 2026): every biplanar graph with alpha <= 2 is 9-colourable (SAT modulo symmetries, Lean 4 checked); settles Gethner-Sulanke's 19-vertex question negatively. Already catalogued; abstract re-read this session. This closes the alpha = 2 instance of the counting route chi >= n/alpha (T3). | SRC-0009/SRC-0037 (grades unchanged) |
| Small orders | ivanspog/earth-moon-alpha2 (unrefereed, AI-produced): alpha <= 2 small-order results; EpsilonPhoenix earth_moon_small_order: n <= 18 9-colourability claims. Neither replayed; not used as filters. | SRC-0063, SRC-0062/0073 (unchanged) |
| Kostochka-Yancey | Edge lower bound for k-critical graphs used in O2/O3. | SRC-0011, SRC-0020 (STATEMENT_INSPECTED, unchanged) |
| Mycielski operations | Classical Mycielskian raises chi by one; generalised Mycielskians (Stiebitz) raise chi via the topological method for suitable bases; level conventions differ between papers (r levels including level 0 versus r + 1 levels). No source found on biplanarity/thickness of Mycielskians; O3 settles it for every base with chi >= 9. | SRC-0036 (unchanged); SRC-0076 new, METADATA_ONLY |
| Topological bounds | Simonyi-Tardos: in every proper colouring of a topologically t-chromatic graph a multicoloured balanced complete bipartite K_{ceil(t/2), floor(t/2)} appears (zig-zag theorem). For t = 10 this is K5,5, which is biplanar: no obstruction. | SRC-0074 new, ABSTRACT_INSPECTED |
| Schrijver graphs | SG(n,k), vertex-critical subgraphs of Kneser graphs with chi = n - 2k + 2 (Schrijver 1978, Nieuw Arch. Wisk. 26:454-461). 10-chromatic members are too dense (O4). | SRC-0075 new, METADATA_ONLY |
| Fractional chromatic number of biplanar graphs | No source found. Related: Gethner-Sulanke independence-ratio open problem (alpha/n < 2/17); Barbados 2018 open problem (independent set >= cn, c > 1/12). | search excerpts only; no SRC |
| Thickness/girth colouring 2024-2026 | Odd-colouring and girth-thickness bounds (arXiv 2403.11555 and others): upper-bound or variant results, not relevant to chi >= 10. | not catalogued (out of scope) |

Novelty: O1 and O3 are short consequences of classical bounds; they may well
be folklore. They are recorded as PROGRAMME_PROVED with no novelty claim.
The E2/A1 extension results concern one seed and are finite computations.
