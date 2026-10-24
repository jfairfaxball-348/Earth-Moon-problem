// bipsat2: SAT-modulo-planarity with OPTIONAL edges (fable-peony, 2026-09-01).
// Edge i of the candidate list has TWO variables: 2i+1 = present in layer 1,
// 2i+2 = present in layer 2 (both false = edge absent; both true allowed).
// Header: p bipsat2 <n> <m> <n_extra_vars> <n_extra_clauses>; extra clauses may
// use vars 2m+1 .. 2m+n_extra_vars.  Derived from bipsat.cpp:
//
// One boolean variable per edge of G (true = layer 1, false = layer 2).
// CaDiCaL 2.x ExternalPropagator (IPASIR-UP) watches the partial assignment;
// whenever a layer's currently-assigned edge set goes nonplanar, a Kuratowski
// subgraph is extracted (Boyer-Myrvold, edge-addition-planarity-suite) and its
// non-monochromatic clause is returned as an external clause. A full model is
// accepted only after both layers pass a from-scratch planarity check.
//
// Instance format (text):
//   p bipsat <n> <m> <n_extra_vars> <n_extra_clauses>
//   e <u> <v>            (m lines; edge i (0-based) <-> SAT var i+1; 0-based vertices)
//   <lit> ... 0          (n_extra_clauses DIMACS clauses; may use vars m+1..m+n_extra_vars)
//
// Output:
//   s SATISFIABLE / s UNSATISFIABLE / s UNKNOWN
//   on SAT: "L1 u-v ..." and "L2 u-v ..." lines with the verified split
//   stats lines prefixed "c "

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <vector>
#include <string>
#include <chrono>
#include <cerrno>
#include <cctype>
#include <fstream>
#include <filesystem>

#include "cadical.hpp"
#include "planar_iface.h"
#include "s032_subdivision.hpp"
#include <io.h>

static double now_s () {
  using namespace std::chrono;
  return duration<double> (steady_clock::now ().time_since_epoch ()).count ();
}

[[noreturn]] static void die (const char *msg) {
  fprintf (stderr, "bipsat FATAL: %s\n", msg);
  fflush (stderr);
  exit (3);
}

// ---------------------------------------------------------------------------
// Planarity checking with Kuratowski extraction
// ---------------------------------------------------------------------------

struct PlanarityChecker {
  PlanCtx *ctx = nullptr;
  int max_edges;
  std::vector<int> flat, kbuf;

  PlanarityChecker (int n_, int max_edges_) : max_edges (max_edges_) {
    ctx = plan_new (n_, max_edges_);
    if (!ctx) die ("plan_new failed");
    flat.reserve (2 * max_edges);
    kbuf.assign (2 * max_edges + 8, 0);
  }
  ~PlanarityChecker () { plan_free (ctx); }
  PlanarityChecker (const PlanarityChecker &) = delete;

  // Returns true if planar. If nonplanar, fills kur_edges with the
  // Kuratowski subgraph's edges (0-based vertex pairs, u < v).
  bool check (const std::vector<std::pair<int, int>> &edges,
              std::vector<std::pair<int, int>> &kur_edges) {
    flat.clear ();
    for (auto &e : edges) {
      flat.push_back (e.first);
      flat.push_back (e.second);
    }
    int klen = 0;
    int r = plan_check (ctx, flat.data (), (int) edges.size (), kbuf.data (),
                        &klen);
    if (r == 1) return true;
    if (r != 0) die ("plan_check internal error");
    kur_edges.clear ();
    for (int i = 0; i < klen; i++)
      kur_edges.emplace_back (kbuf[2 * i], kbuf[2 * i + 1]);
    return false;
  }
};

// Persisted lemmas are untrusted inputs, including after an interrupted write.
// Never add a literal until the ENTIRE clause has been parsed and its geometric
// meaning checked against this instance's edge map. Closing an EOF fragment with
// zero would strengthen a valid Kuratowski clause and can manufacture UNSAT.
struct LemmaLoadStats {
  long loaded = 0, rejected_format = 0, rejected_planar = 0, incomplete = 0;
  bool needs_separator = false;
};

static LemmaLoadStats load_validated_lemmas (
    const char *path, int n, const std::vector<std::pair<int, int>> &edges,
    CaDiCaL::Solver *solver, FILE *validated_out) {
  LemmaLoadStats stats;
  // DrvFS makes thousands of tiny file operations costly; buffer before open.
  std::vector<char> read_buffer (1 << 20);
  std::ifstream input;
  input.rdbuf ()->pubsetbuf (read_buffer.data (), read_buffer.size ());
  input.open (path);
  if (!input) return stats;  // a new run may have no lemma file yet
  const int m = (int) edges.size ();
  PlanarityChecker checker (n, m);
  std::vector<int> clause;
  std::vector<long> seen (m, 0);
  std::vector<std::pair<int, int>> support, kur;
  clause.reserve (m);
  support.reserve (m);
  std::string line;
  long line_number = 0;
  while (std::getline (input, line)) {
    ++line_number;
    stats.needs_separator = input.eof () && !line.empty ();
    clause.clear ();
    support.clear ();
    const char *p = line.c_str ();
    while (std::isspace ((unsigned char) *p)) ++p;
    if (!*p || *p == 'c') continue;
    bool malformed = false, terminated = false;
    int layer = -1;
    while (*p) {
      while (std::isspace ((unsigned char) *p)) ++p;
      if (!*p) break;
      char *end = nullptr;
      errno = 0;
      long lit = std::strtol (p, &end, 10);
      if (errno == ERANGE || end == p || (*end && !std::isspace ((unsigned char) *end))) {
        malformed = true;
        break;
      }
      p = end;
      if (lit == 0) {
        terminated = true;
        while (std::isspace ((unsigned char) *p)) ++p;
        if (*p) malformed = true;  // our writer emits one clause per line
        break;
      }
      // Generated theory clauses contain only negative presence literals from
      // one layer. Reject SAT auxiliaries, mixed layers, and duplicate edges.
      if (lit >= 0 || lit < -2L * m) { malformed = true; break; }
      int v = (int) -lit;
      int this_layer = (v - 1) & 1;
      int edge_index = (v - 1) / 2;
      if ((layer >= 0 && layer != this_layer) || seen[edge_index] == line_number) {
        malformed = true;
        break;
      }
      layer = this_layer;
      seen[edge_index] = line_number;
      clause.push_back ((int) lit);
      support.push_back (edges[edge_index]);
    }
    if (malformed) { ++stats.rejected_format; continue; }
    if (!terminated) { ++stats.incomplete; continue; }
    // Nonplanarity is sufficient; a subdivision need not be minimal. This also
    // detects stale, reordered, or foreign variable maps without trusting a hash.
    if (support.size () < 9 || checker.check (support, kur)) {
      ++stats.rejected_planar;
      continue;
    }
    if (solver) {
      for (int lit : clause) solver->add (lit);
      solver->add (0);
    }
    if (validated_out) {
      for (int lit : clause) fprintf (validated_out, "%d ", lit);
      fputs ("0\n", validated_out);
    }
    ++stats.loaded;
  }
  if (input.bad ()) die ("error reading lemma file");
  return stats;
}

// ---------------------------------------------------------------------------
// The propagator
// ---------------------------------------------------------------------------

struct BipPropagator : CaDiCaL::ExternalPropagator {
  int n, m;
  std::vector<std::pair<int, int>> edges; // edge index -> (u,v), 0-based
  std::vector<std::vector<int>> edge_var; // (u,v) -> var (1..m), 0 if absent

  // mirrored trail
  std::vector<int8_t> val;   // var -> {0 unassigned, +1 layer1, -1 layer2}
  std::vector<int> trail;    // assigned vars in order
  std::vector<size_t> level_marks;

  int cnt[2] = {0, 0};       // current edge count per layer (0 = L1/true, 1 = L2/false)
  bool dirty[2] = {false, false};
  bool conflict_outstanding = false;

  std::vector<std::vector<int>> pending; // external clauses waiting for delivery
  std::vector<int> deliver;              // clause being streamed out
  size_t deliver_pos = 0;

  PlanarityChecker checker;
  std::vector<std::pair<int, int>> scratch_edges, kur;

  // lemma persistence: every external clause is a permanently valid theory lemma,
  // so it is appended here as it is derived and reloaded on the next run.
  FILE *lemma_out = nullptr;
  std::vector<char> lemma_buffer;
  long n_lemmas_written = 0, n_lemmas_loaded = 0;

  void record_lemma (const std::vector<int> &clause) {
    if (!lemma_out) return;
    for (int lit : clause) fprintf (lemma_out, "%d ", lit);
    fputs ("0\n", lemma_out);
    ++n_lemmas_written;
    if (fflush(lemma_out)) die("S032 lemma flush failed");
  }

  // stats
  long n_checks = 0, n_nonplanar = 0, n_clauses_added = 0, n_model_checks = 0;
  long n_model_rejects = 0, n_renotify = 0;
  double check_time = 0.0;

  // last accepted model (the split)
  std::vector<int8_t> model_val;

  BipPropagator (int n_, int m_, const std::vector<std::pair<int, int>> &edges_)
      : n (n_), m (m_), edges (edges_), checker (n_, m_) {
    val.assign (2 * m + 1, 0);
    edge_var.assign (n, std::vector<int> (n, 0));
    for (int i = 0; i < m; i++) {
      auto [u, v] = edges[i];
      edge_var[u][v] = edge_var[v][u] = i + 1;
    }
  }

  ~BipPropagator () {
    // Enumeration can return before main's normal close. Flush while the
    // owned stdio buffer is still alive (before member destruction).
    if (lemma_out) fclose (lemma_out);
  }

  void collect_layer (int layer, std::vector<std::pair<int, int>> &out) {
    out.clear ();
    for (int i = 0; i < m; i++)
      if (val[2 * i + 1 + layer] > 0) out.push_back (edges[i]);
  }

  // Check one layer's current partial edge set; enqueue Kuratowski clause if bad.
  void check_layer (int layer) {
    double t0 = now_s ();
    collect_layer (layer, scratch_edges);
    n_checks++;
    bool planar = checker.check (scratch_edges, kur);
    check_time += now_s () - t0;
    dirty[layer] = false;
    if (planar) return;
    n_nonplanar++;
    std::vector<int> clause;
    clause.reserve (kur.size ());
    for (auto &e : kur) {
      int v = edge_var[e.first][e.second];
      if (!v) die ("Kuratowski edge not in G - impossible");
      clause.push_back (-(2 * (v - 1) + 1 + layer));
    }
    if (!s032_subdivision(n, kur)) die("S032 independent subdivision guard rejected certificate");
    record_lemma (clause);
    pending.push_back (std::move (clause));
    conflict_outstanding = true;
  }

  void maybe_check () {
    if (conflict_outstanding) return;
    for (int layer = 0; layer < 2; layer++)
      if (dirty[layer] && cnt[layer] >= 9) {
        check_layer (layer);
        if (conflict_outstanding) return;
      }
  }

  // ---- notifications ----

  void notify_assignment (const std::vector<int> &lits) override {
    for (int lit : lits) {
      int v = abs (lit);
      if (v > 2 * m) continue; // only edge vars are observed
      int8_t s = lit > 0 ? 1 : -1;
      if (val[v] == s) { n_renotify++; continue; }
      if (val[v] != 0) die ("contradictory re-notification without backtrack");
      val[v] = s;
      trail.push_back (v);
      if (s > 0) {
        int layer = (v - 1) & 1;
        cnt[layer]++;
        dirty[layer] = true;
      }
    }
    maybe_check ();
  }

  void notify_new_decision_level () override {
    level_marks.push_back (trail.size ());
  }

  void notify_backtrack (size_t new_level) override {
    if (new_level >= level_marks.size ()) return;
    size_t keep = level_marks[new_level];
    while (trail.size () > keep) {
      int v = trail.back ();
      trail.pop_back ();
      if (val[v] > 0) cnt[(v - 1) & 1]--;
      val[v] = 0;
    }
    level_marks.resize (new_level);
    conflict_outstanding = false;
    dirty[0] = dirty[1] = false; // removal cannot create nonplanarity
  }

  // ---- model check ----

  bool cb_check_found_model (const std::vector<int> &model) override {
    n_model_checks++;
    std::vector<int8_t> mv (2 * m + 1, 0);
    for (int lit : model) {
      int v = abs (lit);
      if (v <= 2 * m) mv[v] = lit > 0 ? 1 : -1;
    }
    for (int i = 1; i <= 2 * m; i++)
      if (!mv[i]) die ("model leaves an edge variable unassigned");
    for (int layer = 0; layer < 2; layer++) {
      scratch_edges.clear ();
      for (int i = 0; i < m; i++)
        if (mv[2 * i + 1 + layer] > 0) scratch_edges.push_back (edges[i]);
      double t0 = now_s ();
      n_checks++;
      bool planar = checker.check (scratch_edges, kur);
      check_time += now_s () - t0;
      if (!planar) {
        n_nonplanar++;
        n_model_rejects++;
        std::vector<int> clause;
        for (auto &e : kur) {
          int v = edge_var[e.first][e.second];
          if (!v) die ("Kuratowski edge not in G - impossible");
          clause.push_back (-(2 * (v - 1) + 1 + layer));
        }
        if (!s032_subdivision(n, kur)) die("S032 independent subdivision guard rejected certificate");
    record_lemma (clause);
        pending.push_back (std::move (clause));
        conflict_outstanding = true;
        return false;
      }
    }
    model_val = mv;
    return true;
  }

  // ---- external clause delivery ----

  bool cb_has_external_clause (bool &is_forgettable) override {
    is_forgettable = false;
    if (pending.empty ()) return false;
    deliver = std::move (pending.back ());
    pending.pop_back ();
    deliver_pos = 0;
    n_clauses_added++;
    return true;
  }

  int cb_add_external_clause_lit () override {
    if (deliver_pos < deliver.size ()) return deliver[deliver_pos++];
    if (pending.empty ()) conflict_outstanding = false;
    return 0;
  }

  int cb_decide () override { return 0; }
  int cb_propagate () override { return 0; }
  int cb_add_reason_clause_lit (int) override { return 0; }
};

// ---------------------------------------------------------------------------


#include "s045_main.hpp"
