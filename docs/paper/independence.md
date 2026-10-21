# Exporter and kernel independence (paper Section 8)

Paper prep 4, Task 4, 2026-10-21.

- **Source:** Comparator at d03acab154d269c06e60e4de7e4cc85deebff94b (tag v4.34.0), `/root/tools/comparator` in WSL. Read-only.
- **Quoted lines:** `Main.lean` at that commit; the excerpt is saved as `results/2026-10-21-paper-prep-4/comparator-main-excerpt.txt`.
- **Labels:** COMPUTED = read from source; INFERRED = reasoning.

## (a) How each kernel receives declarations

COMPUTED. The pipeline is `compareIt` (Main.lean:304–317):

1. **Build the challenge module and export it.**
   - `safeLakeBuild challengeModule` (114–132) runs `lake build`.
   - `safeExport challengeModule exportTargets` (134–150) then runs **lean4export** in the landrun sandbox: `lean4export <module> -- <decls…>`, with `LEAN_ABORT_ON_PANIC=1`. Its stdout is captured as a string.
   - `exportTargets` = builtin targets ++ theorem_names ++ permitted_axioms ++ primitive targets ++ definition_names (305–306).
2. **Build and export the solution module** in the same way (312–314).
3. **Check, in `verifyMatch` (288–302):**
   - Both export strings are parsed by `Export.parseStream` (290–291), from lean4export's `Export/Parse.lean` (`def parseStream`, line 496 in that package).
   - `Comparator.compareAt` matches the statements on the parsed exports (295).
   - `Comparator.checkAxioms` checks the solution's axioms against `permitted_axioms` (296).
   - Then each external kernel runs (298–299), and then the built-in Lean kernel (300).

**Lean kernel** (`runBuiltinKernel`, 212–239). It does **not** check the elaborated environment that `lake build` produced.
- It starts from `Lean.mkEmptyEnvironment` and **replays the constants parsed from the solution's lean4export output** (`kernelEnv.replay kernelConstMap`, line 222). `Quot.mk`, `Quot.lift` and `Quot.ind` are erased first and re-checked afterwards (216–239).

**nanoda** (`runExternalKernel`, 152–210; registered by `M.run`, 347–351).
- Comparator writes **the same solution export string** (`solutionExport`) to a temp file, plus a nanoda config: permitted axioms, `unpermitted_axiom_hard_error` true, `num_threads` 4, nat and string extensions on.
- It runs `nanoda_bin <config>` through landrun with an empty environment pass-list (`envPass := #[]`).
- nanoda parses the export file itself.
- nanoda is enabled only when the config says `"enable_nanoda": true`: `cfg.enable_nanoda?.getD false` (347). A config with no nanoda key runs with nanoda off.

## (b) Exporter

- **COMPUTED:** the exporter is **lean4export**, commit **076e8e57707e813375e8f9da8bf989799ace9680** (tag v4.34.0).
  - It is Comparator's only Lake dependency (`lakefile.toml`, `[[require]] lean4export`, rev "master", locked in `lake-manifest.json` at 076e8e5).
  - The executable that ran is `/usr/local/bin/lean4export`, sha256 8c5d64ba68f4d3a68b3bcb7e1c5f188e35ae573b29470b8d4530a62324c9ddd1, built from `/root/tools/lean4export` at the same commit (results/2026-10-20-paper-prep/task4-provenance-commands.txt).
- **COMPUTED: both kernels consume the same exported file contents.** Lean's kernel gets the solution export after Comparator's parse (`Export.parseStream` → `ExportedEnv` → `replay`). nanoda gets the identical string as a file and parses it with its own parser.
- **COMPUTED: the challenge export is used only for statement matching**, not by either kernel.

## (c) Components both kernel checks depend on

| Component | Shared by both kernels? | Basis |
|---|---|---|
| Lean elaborator (Lean 4.34.1, commit 5045d005), which produces the `.olean` files that lean4export reads | yes | COMPUTED: both kernels see only lean4export's output, which is read from the built modules (Main.lean:114–150). |
| lean4export 076e8e5 (writer) | yes | COMPUTED: one export string feeds both kernels (Main.lean:298–300, 152–210, 212–239). |
| lean4export's parser (`Export/Parse.lean`) | Lean kernel only; nanoda has its own parser | COMPUTED for the Lean side (290–291). INFERRED for nanoda (it reads the file path in its config; its parser is in nanoda_lib, not read here). |
| Comparator's statement matching (`Comparator.compareAt`) and axiom check (`Comparator.checkAxioms`) | yes: they run once, before either kernel, on the parsed exports | COMPUTED (295–296). Neither kernel re-checks the challenge statement; a defect here affects both verdicts equally. |
| Lean toolchain 4.34.1 (elaboration, and the Lean kernel itself, linked into the comparator binary) | Lean kernel yes; nanoda no (Rust, nanoda_lib 3a24072 / f67473b) | INFERRED from the build setup: comparator built with v4.34.1 (docs/reproduce.md; results/2026-10-08-lean-comparator-wsl.txt). |
| landrun 811cfff (sandbox) and the systemd-run network block | yes (environment only) | COMPUTED (buildLandrunArgs, 80–86; wsl-comparator/67_corpus_run.sh). |

**INFERRED, what "two kernels" covers.**
- It is independence of the type checker only.
- A fault in the elaborator's output, in lean4export's writer, or in Comparator's statement matching or axiom check would reach both kernels identically.
- The nanoda side additionally avoids Comparator's (lean4export's) parser.
