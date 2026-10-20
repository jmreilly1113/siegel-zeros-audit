import StatementChecks.Challenges.DirichletSevenEighths

/-! Non-vacuity checks for `OAI.DirichletCharacter.LFunction_ne_zero_of_seven_eighths_lt_re`
(challenge side only). -/

namespace StatementChecks.Dirichlet

/-- A nonprincipal Dirichlet character mod 4: Mathlib's `χ₄` with values cast into `ℂ`. -/
noncomputable def chi4 : DirichletCharacter ℂ 4 := ZMod.χ₄.ringHomComp (Int.castRingHom ℂ)

theorem chi4_three : chi4 3 = -1 := by
  simp [chi4, MulChar.ringHomComp_apply]

theorem chi4_ne_one : chi4 ≠ 1 := by
  intro h
  have h3 : chi4 3 = 1 := by
    rw [h]
    exact MulChar.one_apply_coe (ZMod.unitOfCoprime 3 (by norm_num))
  rw [chi4_three] at h3
  norm_num at h3

/-- 5a. Every hypothesis is satisfiable, for a nonprincipal and for the principal character. -/
theorem hyps_nonprincipal : (7 / 8 : ℝ) < (2 : ℂ).re ∧ ¬ (chi4 = 1 ∧ (2 : ℂ) = 1) :=
  ⟨by norm_num, fun h => chi4_ne_one h.1⟩

theorem hyps_principal :
    (7 / 8 : ℝ) < (2 : ℂ).re ∧ ¬ ((1 : DirichletCharacter ℂ 4) = 1 ∧ (2 : ℂ) = 1) :=
  ⟨by norm_num, fun h => by norm_num at h⟩

/-- 5b. For `re s > 1` the L-function is the Dirichlet series (Mathlib). -/
theorem eq_dirichlet_series {N : ℕ} [NeZero N] (χ : DirichletCharacter ℂ N) {s : ℂ}
    (hs : 1 < s.re) : DirichletCharacter.LFunction χ s = LSeries (fun n => χ n) s :=
  DirichletCharacter.LFunction_eq_LSeries χ hs

/-- 5b. The L-function of the mod-1 character is `riemannZeta`, which has a zero at `-2`: the
conclusion is not trivially true. -/
theorem modOne_has_zero (χ : DirichletCharacter ℂ 1) : DirichletCharacter.LFunction χ (-2) = 0 := by
  rw [DirichletCharacter.LFunction_modOne_eq]
  simpa using riemannZeta_neg_two_mul_nat_add_one 0

end StatementChecks.Dirichlet

#print axioms StatementChecks.Dirichlet.chi4_ne_one
#print axioms StatementChecks.Dirichlet.hyps_nonprincipal
#print axioms StatementChecks.Dirichlet.hyps_principal
#print axioms StatementChecks.Dirichlet.eq_dirichlet_series
#print axioms StatementChecks.Dirichlet.modOne_has_zero
