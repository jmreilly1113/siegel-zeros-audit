import StatementChecks.HeckeHolo

/-! Statement check 5a for Hecke: an explicit nontrivial `Character` exists. Modulus `(7)`;
`χ(z) = (N z / 7)`, the quadratic character mod 7 of the norm, built from the two ring maps
`O → ZMod 7` sending `ω ↦ 2` and `ω ↦ 4` (the roots of `X² + X + 1` mod 7). Challenge-side definitions
only. -/

open OAI.SevenEighths OAI.SevenEighths.HeckeFamily Polynomial
open IsCyclotomicExtension.Rat.Three

namespace StatementChecks.HeckeNontrivial

local notation "hζ" => IsCyclotomicExtension.zeta_spec 3 ℚ K

instance : Fact (Nat.Prime 7) := ⟨by norm_num⟩

lemma omega_sq : omega ^ 2 + omega + 1 = 0 := by
  have := eta_sq_add_eta_add_one (hζ)
  simpa [omega] using this

/-- The minimal polynomial of `ω` over `ℤ` is `X² + X + 1`. -/
lemma minpoly_omega : minpoly ℤ ((hζ).integralPowerBasis.gen) = X ^ 2 + X + 1 := by
  have hg : (hζ).integralPowerBasis.gen = omega := by
    simp [omega, IsPrimitiveRoot.integralPowerBasis_gen]
  have hmonic : (X ^ 2 + X + 1 : ℤ[X]).Monic := by monicity!
  have hdeg : (X ^ 2 + X + 1 : ℤ[X]).natDegree = 2 := by compute_degree!
  have hroot : aeval ((hζ).integralPowerBasis.gen) (X ^ 2 + X + 1 : ℤ[X]) = 0 := by
    rw [hg]; simp [omega_sq]
  have hdvd := minpoly.isIntegrallyClosed_dvd ((hζ).integralPowerBasis.isIntegral_gen) hroot
  have hmd : (minpoly ℤ ((hζ).integralPowerBasis.gen)).natDegree = 2 := by
    rw [(hζ).integralPowerBasis.natDegree_minpoly]
    simp [IsPrimitiveRoot.integralPowerBasis_dim, Nat.totient_prime Nat.prime_three]
  exact (eq_of_monic_of_dvd_of_natDegree_le (minpoly.monic (hζ).integralPowerBasis.isIntegral_gen)
    hmonic hdvd (by rw [hdeg, hmd])).symm

/-- The two ring maps `O → ZMod 7`. -/
noncomputable def ρ (y : ZMod 7) (hy : y ^ 2 + y + 1 = 0) : O →ₐ[ℤ] ZMod 7 :=
  (hζ).integralPowerBasis.lift y (by rw [minpoly_omega]; simpa using hy)

lemma ρ_omega (y : ZMod 7) (hy : y ^ 2 + y + 1 = 0) : ρ y hy omega = y := by
  have hg : (hζ).integralPowerBasis.gen = omega := by
    simp [omega, IsPrimitiveRoot.integralPowerBasis_gen]
  rw [← hg]; exact PowerBasis.lift_gen _ _ _

lemma h2 : (2 : ZMod 7) ^ 2 + 2 + 1 = 0 := by decide
lemma h4 : (4 : ZMod 7) ^ 2 + 4 + 1 = 0 := by decide

noncomputable abbrev ρ₁ := ρ 2 h2
noncomputable abbrev ρ₂ := ρ 4 h4

/-- The modulus `(7)`. -/
noncomputable abbrev M7 : Ideal O := Ideal.span {(7 : O)}

lemma ρ_kills (y : ZMod 7) (hy : y ^ 2 + y + 1 = 0) : ∀ a ∈ M7, (ρ y hy).toRingHom a = 0 := by
  intro a ha
  obtain ⟨b, rfl⟩ := Ideal.mem_span_singleton'.mp ha
  simp only [AlgHom.toRingHom_eq_coe, RingHom.coe_coe, map_mul]
  have : (ρ y hy) (7 : O) = 0 := by
    rw [show (7 : O) = algebraMap ℤ O 7 by simp, AlgHom.commutes]; decide
  rw [this, mul_zero]

/-- The two maps on the quotient. -/
noncomputable def ρbar (y : ZMod 7) (hy : y ^ 2 + y + 1 = 0) : O ⧸ M7 →+* ZMod 7 :=
  Ideal.Quotient.lift M7 (ρ y hy).toRingHom (ρ_kills y hy)

/-- `ν(z) = ρ₁(z) ρ₂(z)`, i.e. the norm of `z` mod 7. -/
noncomputable def ν : O ⧸ M7 →* ZMod 7 :=
  (ρbar 2 h2).toMonoidHom * (ρbar 4 h4).toMonoidHom

/-- The quadratic character mod 7, with values in `ℂ`. -/
noncomputable def ψ7 : MulChar (ZMod 7) ℂ := (quadraticChar (ZMod 7)).ringHomComp (Int.castRingHom ℂ)

noncomputable def residue7 : MulChar (O ⧸ M7) ℂ :=
  MulChar.ofUnitHom (ψ7.toUnitHom.comp (Units.map ν))

lemma residue7_apply_unit (v : (O ⧸ M7)ˣ) : residue7 v = ψ7 (ν v) := by
  simp [residue7]

lemma ν_mk (z : O) : ν (Ideal.Quotient.mk M7 z) = ρ₁ z * ρ₂ z := rfl

lemma unit_trivial7 (u : Oˣ) : residue7 (Ideal.Quotient.mk M7 (u : O)) = 1 := by
  have hu := Units.mem (hζ) u
  have hval : ρ₁ (u : O) * ρ₂ (u : O) = 1 := by
    have h1 : ρ₁ omega = 2 := ρ_omega 2 h2
    have h2' : ρ₂ omega = 4 := ρ_omega 4 h4
    simp only [List.mem_cons, List.not_mem_nil, or_false] at hu
    rcases hu with h | h | h | h | h | h <;> subst h <;>
      simp [coe_eta, omega, h1, h2'] at * <;> first | decide | (simp [omega] at h1 h2'; rw [h1, h2']; decide)
  have hunit : IsUnit (Ideal.Quotient.mk M7 (u : O)) := (Units.isUnit u).map _
  rw [← hunit.unit_spec, residue7_apply_unit, IsUnit.unit_spec, ν_mk, hval, map_one]

lemma two_add_omega_unit : IsUnit (Ideal.Quotient.mk M7 (2 + omega)) := by
  refine IsUnit.of_mul_eq_one (Ideal.Quotient.mk M7 (5 - 5 * omega)) ?_
  rw [← map_mul, ← map_one (Ideal.Quotient.mk M7), Ideal.Quotient.eq]
  have : (2 + omega) * (5 - 5 * omega) - 1 = 7 * 2 - 5 * (omega ^ 2 + omega + 1) := by ring
  rw [this, omega_sq, mul_zero, sub_zero]
  exact Ideal.mul_mem_right _ _ (Ideal.mem_span_singleton_self _)

lemma residue7_ne_one : residue7 ≠ 1 := by
  intro h
  have hu := two_add_omega_unit
  have h1 : residue7 (Ideal.Quotient.mk M7 (2 + omega)) = 1 := by
    rw [h]; exact MulChar.one_apply hu
  rw [← hu.unit_spec, residue7_apply_unit, hu.unit_spec, ν_mk] at h1
  have e1 : ρ₁ (2 + omega) = 4 := by rw [map_add, map_ofNat, ρ_omega]; decide
  have e2 : ρ₂ (2 + omega) = 6 := by rw [map_add, map_ofNat, ρ_omega]; decide
  rw [e1, e2] at h1
  have hq : quadraticChar (ZMod 7) (4 * 6) = -1 :=
    quadraticChar_neg_one_iff_not_isSquare.mpr (by unfold IsSquare; decide)
  simp [ψ7, MulChar.ringHomComp_apply, hq] at h1
  norm_num at h1

/-- The nontrivial character. -/
noncomputable def chi7 : Character where
  modulus := M7
  modulus_ne_bot := by
    rw [Ne, Ideal.span_singleton_eq_bot]; exact_mod_cast (by norm_num : (7 : ℤ) ≠ 0)
  residue := residue7
  unit_trivial := unit_trivial7
  period := 7
  period_pos := by norm_num
  period_mem := by exact_mod_cast Ideal.mem_span_singleton_self (7 : O)

theorem chi7_nontrivial : chi7.residue ≠ 1 := residue7_ne_one

/-- 5a: the statement's hypotheses hold for `chi7` at every `s` with `7/8 < re s`, including `s = 1`. -/
theorem hyps_chi7 {s : ℂ} (hs : (7 / 8 : ℝ) < s.re) :
    (7 / 8 : ℝ) < s.re ∧ ¬ (chi7.residue = 1 ∧ s = 1) := ⟨hs, fun h => chi7_nontrivial h.1⟩

/-- 5b: its L-function is entire and equals the lattice Dirichlet series for `re s > 1`. -/
theorem chi7_entire : Differentiable ℂ (LFunction chi7) :=
  StatementChecks.HeckeHolo.differentiable_of_ne_one chi7 chi7_nontrivial

theorem chi7_series {s : ℂ} (hs : 1 < s.re) :
    HasSum (fun q : ℤ × ℤ => StatementChecks.HeckeSeries.a' chi7 q /
      ((StatementChecks.HeckeSeries.Qf q.1 q.2 : ℝ) : ℂ) ^ s / 6) (LFunction chi7 s) :=
  StatementChecks.HeckeSeries.LFunction_hasSum chi7 hs

end StatementChecks.HeckeNontrivial

#print axioms StatementChecks.HeckeNontrivial.chi7_nontrivial
#print axioms StatementChecks.HeckeNontrivial.hyps_chi7
#print axioms StatementChecks.HeckeNontrivial.chi7_entire
#print axioms StatementChecks.HeckeNontrivial.chi7_series
