import OAI.NumberTheory.SiegelZeros.Main

/-!
Stand-in for the comparator (which needs Linux/landrun).
1. The two challenge statements from ComparatorChallenges/SiegelZeros.lean are restated
   verbatim (only the theorem names changed) and proved by citing the solution's theorems.
   If the solution's types differed from the challenge's, these would fail to elaborate.
2. `#print axioms` lists every axiom the solution theorems depend on.
-/

namespace SiegelCheck

theorem challenge_exists_absolute_real_zero_gap :
    ∃ c : ℝ, 0 < c ∧
      ∀ (q : ℕ) [NeZero q], 3 ≤ q →
      ∀ χ : DirichletCharacter ℂ q,
        χ.IsPrimitive → χ ≠ 1 → (∀ a : ZMod q, (χ a).im = 0) →
        ∀ β : ℝ, 0 < β → β < 1 → χ.LFunction (β : ℂ) = 0 →
          c ≤ (1 - β) * Real.log (q : ℝ) :=
  OAI.SiegelZeros.WeightedTorusJets.exists_absolute_real_zero_gap

theorem challenge_dirichletRealZeroBound_proof :
    ∃ c : ℝ, 0 < c ∧ ∀ (q : ℕ) [NeZero q], 3 ≤ q →
      ∀ χ : DirichletCharacter ℂ q,
        χ.IsPrimitive → χ ≠ 1 → (∀ a : ZMod q, (χ a).im = 0) →
        ∀ β : ℝ,
          (0 < β ∧ β < 1 ∧ DirichletCharacter.LFunction χ (β : ℂ) = 0) →
            c ≤ (1 - β) * Real.log (q : ℝ) :=
  OAI.SiegelZeros.WeightedTorusJets.dirichletRealZeroBound_proof

end SiegelCheck

#print axioms OAI.SiegelZeros.WeightedTorusJets.exists_absolute_real_zero_gap
#print axioms OAI.SiegelZeros.WeightedTorusJets.dirichletRealZeroBound_proof
#print axioms OAI.SiegelZeros.WeightedTorusJets.dirichlet_real_zero_bound
#print axioms SiegelCheck.challenge_exists_absolute_real_zero_gap
