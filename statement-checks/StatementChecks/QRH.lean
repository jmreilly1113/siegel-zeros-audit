import StatementChecks.Challenges.QuasiRiemannHypothesis

/-! Non-vacuity checks for `OAI.riemannZeta_ne_zero_of_seven_eighths_lt_re` (challenge side only). -/

namespace StatementChecks.QRH

/-- 5a. The hypothesis is satisfiable: `s = 2` meets `7/8 < re s`. -/
theorem hyp_satisfiable : (7 / 8 : ℝ) < (2 : ℂ).re := by norm_num

/-- 5b. `riemannZeta` is not identically nonzero: it has the trivial zero `-2`, so the conclusion
`riemannZeta s ≠ 0` is a real restriction on `s`. -/
theorem has_trivial_zero : riemannZeta (-2) = 0 := by
  simpa using riemannZeta_neg_two_mul_nat_add_one 0

/-- 5b. For `re s > 1`, `riemannZeta` is the Dirichlet series `∑ 1/n^s` (Mathlib). -/
theorem eq_dirichlet_series {s : ℂ} (hs : 1 < s.re) :
    riemannZeta s = ∑' n : ℕ, 1 / (n : ℂ) ^ s :=
  zeta_eq_tsum_one_div_nat_cpow hs

/-- Step 3. `s = 1` is not excluded by the statement; there Mathlib's assigned (junk) value is
`(γ - log (4π)) / 2`, which is nonzero. -/
theorem junk_at_one :
    riemannZeta 1 = (Real.eulerMascheroniConstant - Complex.log (4 * Real.pi)) / 2 :=
  riemannZeta_one

theorem junk_at_one_ne_zero : riemannZeta 1 ≠ 0 := riemannZeta_one_ne_zero

end StatementChecks.QRH

#print axioms StatementChecks.QRH.hyp_satisfiable
#print axioms StatementChecks.QRH.has_trivial_zero
#print axioms StatementChecks.QRH.eq_dirichlet_series
#print axioms StatementChecks.QRH.junk_at_one
#print axioms StatementChecks.QRH.junk_at_one_ne_zero
