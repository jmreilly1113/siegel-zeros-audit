# Draft: follow-up comment for grwtsk/openai-math issue #40

Draft for Joe to post. Links point at the tag `reviewer-packet-v1.1`, which does not exist until this is committed and tagged.

---

On the open item "external declaration overlap unresolved": since Mathlib enters both routes as one import root, we measured overlap at the level of declarations instead of modules.

**Inputs.** All are openai/math `adc7f12`; the pinned paths are unchanged at `fd4aeeb`. Each is a lean4export (v4.34.0) dump of one theorem's dependency closure:
- Route 1: `exists_absolute_real_zero_gap`.
- Route 2 original: `dirichletRealZeroBound_proof`.
- Route 2 rerouted: `dirichletRealZeroBound_proof` in the clone where OAI's Corollary 4 is replaced by the paper's Lemma 3. This is the version the official comparator accepted with nanoda.

For each dump, a Python reimplementation of our `#find_deps` traversal reproduces the counts we reported earlier exactly: 107,760, 116,314 and 92,658. The rest of each dump is only recursors and constructors that nothing references.

**Numbers** (referenced-only closures, exact set operations):

| A | B | \|A\| | \|B\| | \|A∩B\| | Jaccard | shared OAI declarations |
|---|---|---:|---:|---:|---:|---:|
| route 1 | route 2 original | 107,760 | 116,314 | 102,553 | 0.844 | 0 |
| route 1 | route 2 rerouted | 107,760 | 92,658 | 82,701 | 0.703 | 0 |
| route 2 original | route 2 rerouted | 116,314 | 92,658 | 92,253 | 0.790 | 575 |

- The route 1 ∩ route 2 shared set is Mathlib, core and root-level names only. By name prefix, which is approximate: about 82,600 Mathlib-style, 10,700 core-namespace and 9,200 root-level names.
- No OAI declaration is shared between the two routes, public or private. Private names record their defining module, so this check is exact for them.
- Without auto-generated names (`_proof_`, `match_`, `.rec`, `eq_` and similar), route 1 ∩ route 2 original is 63,691 shared names, with Jaccard 0.847.
- Rerouting removes 24,061 names from route 2 and adds 405. The removed names are mostly CategoryTheory (6,901), AlgebraicGeometry (3,035) and 1,420 OAI names; the added ones include our 68 `Lemma3.*` declarations.

**Limits** (our inference, not a measurement):
- Shared declarations measure a shared trusted base. They do not measure mathematical dependence, and they say nothing about whether the two routes are independent proofs.
- Zero shared OAI declarations next to a large shared Mathlib base is what one would expect from two proofs of related statements built on the same library. We don't read the numbers as showing the routes are either independent or dependent.
- The split by name prefix is approximate. Mathlib extends core namespaces such as `Nat` and `List`, and the dumps don't record defining modules for public names.

**Files** (tag `reviewer-packet-v1.1`):
- Results: https://github.com/jmreilly1113/siegel-zeros-audit/blob/reviewer-packet-v1.1/results/2026-10-09-route-declaration-overlap.txt
- Script: https://github.com/jmreilly1113/siegel-zeros-audit/blob/reviewer-packet-v1.1/src/route_overlap.py, which runs on the name lists in `results/2026-10-09-closure-names/`, so the computation can be repeated without Lean.
- Export of the rerouted closure: https://github.com/jmreilly1113/siegel-zeros-audit/blob/reviewer-packet-v1.1/results/2026-10-09-rerouted-closure-export.txt
