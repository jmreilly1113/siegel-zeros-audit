import Lake
open Lake DSL

-- Trimmed build of the Siegel-zero formalization from openai/math @ adc7f12 (lean/).
-- Sources are byte-identical copies:
--   OAI/NumberTheory/SiegelZeros/**                from lean/OAI/NumberTheory/SiegelZeros/
--   ComparatorChallenges/SiegelZeros.{lean,json}   from lean/ComparatorChallenges/
--   PrimeNumberTheoremAnd/SiegelZeros/*.lean       new files created by lean/patches/PrimeNumberTheoremAnd-lean4341.patch
-- Only Mathlib is required, at the same commit as lean/lake-manifest.json.
package OAISiegel where
  leanOptions := #[⟨`autoImplicit, false⟩]

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "d13f23b723b8a846827a245b89c10fc7d3f11612"

-- Same options as the patched PrimeNumberTheoremAnd lakefile (lean_lib PrimeNumberTheoremAnd: autoImplicit = false).
lean_lib PrimeNumberTheoremAndSiegelZeros where
  roots := #[`PrimeNumberTheoremAnd.SiegelZeros.HadamardSupport]
  globs := #[.submodules `PrimeNumberTheoremAnd.SiegelZeros]

@[default_target] lean_lib OAISiegelZeros where
  roots := #[`OAI.NumberTheory.SiegelZeros.Main]
  globs := #[.submodules `OAI.NumberTheory.SiegelZeros]

lean_lib ComparatorChallenges where
  globs := #[.submodules `ComparatorChallenges]
