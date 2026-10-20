import StatementChecks.Challenges.HeckeSevenEighths

/-! Non-vacuity and holomorphy checks for
`OAI.SevenEighths.HeckeFamily.LFunction_ne_zero_of_seven_eighths_lt_re` (challenge side only). -/

open OAI.SevenEighths OAI.SevenEighths.HeckeFamily OAI.SevenEighths.HeckeTheta

namespace StatementChecks.Hecke

/-- The trivial character with modulus the unit ideal (its L-function should be the Dedekind zeta
function of `ℚ(√-3)`). -/
noncomputable def trivialTop : Character where
  modulus := ⊤
  modulus_ne_bot := top_ne_bot
  residue := 1
  unit_trivial u := MulChar.one_apply ((Units.isUnit u).map (Ideal.Quotient.mk (⊤ : Ideal O)))
  period := 1
  period_pos := one_pos
  period_mem := Submodule.mem_top

/-- 5a. Every hypothesis is satisfiable (trivial character, `s = 2`). -/
theorem hyps_trivialTop :
    (7 / 8 : ℝ) < (2 : ℂ).re ∧ ¬ (trivialTop.residue = 1 ∧ (2 : ℂ) = 1) :=
  ⟨by norm_num, fun h => by norm_num at h⟩

/-- Joe's item 1, holomorphy: for every character, the defined L-function is complex
differentiable at every `s ≠ 0, 1`. Uses Mathlib's `WeakFEPair.differentiableAt_Λ`,
`Complex.differentiable_one_div_Gamma` and differentiability of `π ^ s`. -/
theorem differentiableAt_LFunction (χ : Character) {s : ℂ} (h0 : s ≠ 0) (h1 : s ≠ 1) :
    DifferentiableAt ℂ (LFunction χ) s := by
  have hk : (pair (coefficients χ)).k = 1 := rfl
  have hΛ : DifferentiableAt ℂ (pair (coefficients χ)).Λ s :=
    (pair (coefficients χ)).differentiableAt_Λ (Or.inl h0) (Or.inl (by rw [hk]; exact_mod_cast h1))
  have hpi : DifferentiableAt ℂ (fun z : ℂ => (Real.pi : ℂ) ^ z) s :=
    (differentiableAt_id.const_cpow (Or.inl (Complex.ofReal_ne_zero.mpr Real.pi_ne_zero)))
  have hg : DifferentiableAt ℂ (fun z : ℂ => (Complex.Gamma z)⁻¹) s := by
    simpa [one_div] using Complex.differentiable_one_div_Gamma s
  have : LFunction χ = fun z => (Real.pi : ℂ) ^ z * (Complex.Gamma z)⁻¹ *
      (pair (coefficients χ)).Λ z / 6 := rfl
  rw [this]
  exact ((hpi.mul hg).mul hΛ).div_const 6

/-- Holomorphy at `s = 1` whenever the pole coefficient `g₀` of the theta pair vanishes. -/
theorem differentiableAt_LFunction_one (χ : Character) (hg₀ : (pair (coefficients χ)).g₀ = 0) :
    DifferentiableAt ℂ (LFunction χ) 1 := by
  have hΛ : DifferentiableAt ℂ (pair (coefficients χ)).Λ 1 :=
    (pair (coefficients χ)).differentiableAt_Λ (Or.inl one_ne_zero) (Or.inr hg₀)
  have hpi : DifferentiableAt ℂ (fun z : ℂ => (Real.pi : ℂ) ^ z) 1 :=
    (differentiableAt_id.const_cpow (Or.inl (Complex.ofReal_ne_zero.mpr Real.pi_ne_zero)))
  have hg : DifferentiableAt ℂ (fun z : ℂ => (Complex.Gamma z)⁻¹) 1 := by
    simpa [one_div] using Complex.differentiable_one_div_Gamma 1
  have : LFunction χ = fun z => (Real.pi : ℂ) ^ z * (Complex.Gamma z)⁻¹ *
      (pair (coefficients χ)).Λ z / 6 := rfl
  rw [this]
  exact ((hpi.mul hg).mul hΛ).div_const 6

/-- So the defined L-function is holomorphic on the half-plane `re s > 0` minus `{1}`, for every
character; this covers the strip `7/8 < re s ≤ 1` of the statement except `s = 1`. -/
theorem differentiableOn_halfPlane (χ : Character) :
    DifferentiableOn ℂ (LFunction χ) {s : ℂ | 0 < s.re ∧ s ≠ 1} := by
  intro s hs
  have h0 : s ≠ 0 := by rintro rfl; simp at hs
  exact (differentiableAt_LFunction χ h0 hs.2).differentiableWithinAt

end StatementChecks.Hecke

#print axioms StatementChecks.Hecke.hyps_trivialTop
#print axioms StatementChecks.Hecke.differentiableAt_LFunction
#print axioms StatementChecks.Hecke.differentiableAt_LFunction_one
#print axioms StatementChecks.Hecke.differentiableOn_halfPlane
