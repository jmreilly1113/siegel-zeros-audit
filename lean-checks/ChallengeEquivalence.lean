import Mathlib

/-! The two theorem statements of the SiegelZeros challenge (openai/math lean/ComparatorChallenges/SiegelZeros.lean,
lines 8-14 and 19-25, file sha256 bedaac02..., identical at adc7f12 and fd4aeeb) are equivalent.
Each Prop below is the statement text of the challenge, copied verbatim from the line after `theorem ... :` to just before
`:= by`. Like the challenge file, this file imports Mathlib only. -/

namespace ChallengeEquivalence

/-- SiegelZeros.lean:9-14 (exists_absolute_real_zero_gap). -/
def ExistsAbsoluteRealZeroGap : Prop :=
    ∃ c : ℝ, 0 < c ∧
      ∀ (q : ℕ) [NeZero q], 3 ≤ q →
      ∀ χ : DirichletCharacter ℂ q,
        χ.IsPrimitive → χ ≠ 1 → (∀ a : ZMod q, (χ a).im = 0) →
        ∀ β : ℝ, 0 < β → β < 1 → χ.LFunction (β : ℂ) = 0 →
          c ≤ (1 - β) * Real.log (q : ℝ)

/-- SiegelZeros.lean:20-25 (WeightedTorusJets.dirichletRealZeroBound_proof). -/
def DirichletRealZeroBound : Prop :=
    ∃ c : ℝ, 0 < c ∧ ∀ (q : ℕ) [NeZero q], 3 ≤ q →
      ∀ χ : DirichletCharacter ℂ q,
        χ.IsPrimitive → χ ≠ 1 → (∀ a : ZMod q, (χ a).im = 0) →
        ∀ β : ℝ,
          (0 < β ∧ β < 1 ∧ DirichletCharacter.LFunction χ (β : ℂ) = 0) →
            c ≤ (1 - β) * Real.log (q : ℝ)

theorem statements_equivalent : ExistsAbsoluteRealZeroGap ↔ DirichletRealZeroBound := by
  constructor
  · rintro ⟨c, hc, h⟩
    refine ⟨c, hc, ?_⟩
    intro q _ hq χ hprim hne hreal β hβ
    exact h q hq χ hprim hne hreal β hβ.1 hβ.2.1 hβ.2.2
  · rintro ⟨c, hc, h⟩
    refine ⟨c, hc, ?_⟩
    intro q _ hq χ hprim hne hreal β h0 h1 hz
    exact h q hq χ hprim hne hreal β ⟨h0, h1, hz⟩

end ChallengeEquivalence

#print axioms ChallengeEquivalence.statements_equivalent
