import StatementChecks.HeckeSeries
import StatementChecks.Hecke

/-! Holomorphy of the challenge's Hecke `LFunction` at `s = 0` and `s = 1` for nontrivial characters,
and the value at `s = 0` for the trivial character of modulus `O`. Challenge-side definitions only. -/

open OAI.SevenEighths OAI.SevenEighths.HeckeFamily OAI.SevenEighths.HeckeTheta
  OAI.SevenEighths.EisensteinTheta OAI.SevenEighths.ThetaProduct
open StatementChecks.HeckeSeries

namespace StatementChecks.HeckeHolo

/-- If the modulus is the unit ideal, the only character is the trivial one. -/
lemma residue_eq_one_of_top (χ : Character) (h : χ.modulus = ⊤) : χ.residue = 1 := by
  have : Subsingleton (O ⧸ χ.modulus) := Ideal.Quotient.subsingleton_iff.mpr h
  ext u
  have hu : (u : O ⧸ χ.modulus) = 1 := Subsingleton.elim _ _
  rw [hu, map_one, map_one]

lemma modulus_ne_top (χ : Character) (h : χ.residue ≠ 1) : χ.modulus ≠ ⊤ :=
  fun ht => h (residue_eq_one_of_top χ ht)

/-- For a proper modulus the constant term `f₀ = χ(0)` vanishes. -/
lemma f₀_eq_zero (χ : Character) (hm : χ.modulus ≠ ⊤) : (pair (coefficients χ)).f₀ = 0 := by
  rw [pair_f₀]
  have : Nontrivial (O ⧸ χ.modulus) := Ideal.Quotient.nontrivial_iff.mpr hm
  unfold c elementCoeff
  have h0 : coordinateElement 0 0 = 0 := by simp [coordinateElement]
  rw [h0, map_zero]
  exact χ.residue.map_nonunit not_isUnit_zero

/-- Holomorphy at `s = 0` for every character with a proper modulus (in particular every
nontrivial one). -/
theorem differentiableAt_zero (χ : Character) (hm : χ.modulus ≠ ⊤) :
    DifferentiableAt ℂ (LFunction χ) 0 := by
  have hk : (pair (coefficients χ)).k = 1 := rfl
  have hΛ : DifferentiableAt ℂ (pair (coefficients χ)).Λ 0 :=
    (pair (coefficients χ)).differentiableAt_Λ (Or.inr (f₀_eq_zero χ hm))
      (Or.inl (by rw [hk]; norm_num))
  have hpi : DifferentiableAt ℂ (fun z : ℂ => (Real.pi : ℂ) ^ z) 0 :=
    (differentiableAt_id.const_cpow (Or.inl (Complex.ofReal_ne_zero.mpr Real.pi_ne_zero)))
  have hg : DifferentiableAt ℂ (fun z : ℂ => (Complex.Gamma z)⁻¹) 0 := by
    simpa [one_div] using Complex.differentiable_one_div_Gamma 0
  have : LFunction χ = fun z => (Real.pi : ℂ) ^ z * (Complex.Gamma z)⁻¹ *
      (pair (coefficients χ)).Λ z / 6 := rfl
  rw [this]
  exact ((hpi.mul hg).mul hΛ).div_const 6

/-- The trivial character of modulus `O` at `s = 0`: the definition gives `0` (Mathlib's
`Gamma 0 = 0`), whereas the Dedekind zeta function of `ℚ(√-3)` has value `-1/6` there. This point is
outside the statement's half-plane. -/
theorem trivialTop_at_zero : LFunction StatementChecks.Hecke.trivialTop 0 = 0 := by
  simp [LFunction, continuedLattice, latticeL, Complex.Gamma_zero]

/-! ### `g₀ = 0` for nontrivial characters (orthogonality), hence holomorphy at `s = 1` -/

/-- Every element of `O` is `x + y ω` (integral power basis of `ℤ[ζ₃]`, dimension `φ 3 = 2`). -/
lemma coord_surj (α : O) : ∃ x y : ℤ, coordinateElement x y = α := by
  let hζ := IsCyclotomicExtension.zeta_spec 3 ℚ K
  let pb := hζ.integralPowerBasis
  have hdim : pb.dim = 2 := by
    simp [pb, IsPrimitiveRoot.integralPowerBasis_dim, Nat.totient_prime Nat.prime_three]
  obtain ⟨f, hf, hα⟩ := pb.exists_eq_aeval α
  have hdeg : f.natDegree ≤ 1 := by omega
  refine ⟨f.coeff 0, f.coeff 1, ?_⟩
  have hf2 := Polynomial.eq_X_add_C_of_natDegree_le_one hdeg
  rw [hα]
  conv_rhs => rw [hf2]
  simp only [map_add, map_mul, Polynomial.aeval_C, Polynomial.aeval_X, coordinateElement]
  have hg : pb.gen = omega := by simp [pb, omega, IsPrimitiveRoot.integralPowerBasis_gen]
  rw [hg]
  simp [algebraMap_int_eq]
  ring

variable (χ : Character)

/-- The residue map of the box `[0, N)²` into `O ⧸ modulus`. -/
noncomputable def ψ (ab : Fin χ.period × Fin χ.period) : O ⧸ χ.modulus :=
  Ideal.Quotient.mk χ.modulus (coordinateElement ((ab.1 : ℕ) : ℤ) ((ab.2 : ℕ) : ℤ))

lemma mk_coord_mod (x y : ℤ) (k l : ℤ) :
    Ideal.Quotient.mk χ.modulus (coordinateElement (x + χ.period * k) (y + χ.period * l)) =
      Ideal.Quotient.mk χ.modulus (coordinateElement x y) := by
  rw [Ideal.Quotient.eq]
  have h : coordinateElement (x + χ.period * k) (y + χ.period * l) - coordinateElement x y =
      (χ.period : O) * ((k : O) + (l : O) * omega) := by
    simp only [coordinateElement]; push_cast; ring
  rw [h]; exact Ideal.mul_mem_right _ _ χ.period_mem

lemma coordinateElement_add (x₁ y₁ x₂ y₂ : ℤ) :
    coordinateElement (x₁ + x₂) (y₁ + y₂) = coordinateElement x₁ y₁ + coordinateElement x₂ y₂ := by
  simp only [coordinateElement]; push_cast; ring

lemma fin_add_val (N : ℕ) [NeZero N] (a p : Fin N) :
    ∃ k : ℤ, (((a + p : Fin N) : ℕ) : ℤ) = ((a : ℕ) : ℤ) + ((p : ℕ) : ℤ) + N * k := by
  refine ⟨-((((a : ℕ) + (p : ℕ)) / N : ℕ) : ℤ), ?_⟩
  rw [Fin.val_add]
  have h := congrArg (Nat.cast : ℕ → ℤ) (Nat.mod_add_div ((a : ℕ) + (p : ℕ)) N)
  push_cast at h ⊢
  linarith

lemma ψ_add (ab pq : Fin χ.period × Fin χ.period) : ψ χ (ab + pq) = ψ χ ab + ψ χ pq := by
  obtain ⟨k, hk⟩ := fin_add_val χ.period ab.1 pq.1
  obtain ⟨l, hl⟩ := fin_add_val χ.period ab.2 pq.2
  simp only [ψ, Prod.fst_add, Prod.snd_add]
  rw [hk, hl, mk_coord_mod, coordinateElement_add, map_add]

lemma ψ_surj : Function.Surjective (ψ χ) := by
  intro y
  obtain ⟨z, rfl⟩ := Ideal.Quotient.mk_surjective y
  obtain ⟨x, w, rfl⟩ := coord_surj z
  have hN := HeckeSeries.Npos χ.period
  refine ⟨(⟨(x % χ.period).toNat, by have := Int.emod_lt_of_pos x hN; have := Int.emod_nonneg x hN.ne'; omega⟩,
    ⟨(w % χ.period).toNat, by have := Int.emod_lt_of_pos w hN; have := Int.emod_nonneg w hN.ne'; omega⟩), ?_⟩
  simp only [ψ]
  rw [Int.toNat_of_nonneg (Int.emod_nonneg x hN.ne'), Int.toNat_of_nonneg (Int.emod_nonneg w hN.ne')]
  have h1 := Int.emod_add_mul_ediv x χ.period
  have h2 := Int.emod_add_mul_ediv w χ.period
  conv_rhs => rw [← h1, ← h2]
  rw [mk_coord_mod]

/-- Orthogonality: for a nontrivial character the coefficients sum to zero over the box. -/
lemma sum_coefficients_eq_zero (hχ : χ.residue ≠ 1) :
    ∑ ab : Fin χ.period × Fin χ.period, coefficients χ ab = 0 := by
  classical
  letI : Fintype (O ⧸ χ.modulus) := Fintype.ofSurjective (ψ χ) (ψ_surj χ)
  have hc : ∀ ab, coefficients χ ab = χ.residue (ψ χ ab) := fun _ => rfl
  simp_rw [hc]
  set S := ∑ ab : Fin χ.period × Fin χ.period, χ.residue (ψ χ ab) with hS
  -- translation invariance: S = ∑ χ(ψ ab + y) for every y
  have htrans : ∀ y : O ⧸ χ.modulus, ∑ ab, χ.residue (ψ χ ab + y) = S := by
    intro y
    obtain ⟨pq, rfl⟩ := ψ_surj χ y
    simp_rw [← ψ_add]
    simpa using Equiv.sum_comp (Equiv.addRight pq) (fun ab => χ.residue (ψ χ ab))
  have hsum : (Fintype.card (O ⧸ χ.modulus) : ℂ) * S = 0 := by
    calc (Fintype.card (O ⧸ χ.modulus) : ℂ) * S = ∑ y : O ⧸ χ.modulus, ∑ ab, χ.residue (ψ χ ab + y) := by
          simp [htrans, Finset.card_univ]
      _ = ∑ ab, ∑ y : O ⧸ χ.modulus, χ.residue (ψ χ ab + y) := Finset.sum_comm
      _ = ∑ ab : Fin χ.period × Fin χ.period, (0 : ℂ) := by
          refine Finset.sum_congr rfl (fun ab _ => ?_)
          have h := Equiv.sum_comp (Equiv.addLeft (ψ χ ab)) (fun y => χ.residue y)
          simp only [Equiv.coe_addLeft] at h
          rw [h]
          exact MulChar.sum_eq_zero_of_ne_one hχ
      _ = 0 := by simp
  have hcard : (Fintype.card (O ⧸ χ.modulus) : ℂ) ≠ 0 := by
    exact_mod_cast Fintype.card_ne_zero
  exact (mul_eq_zero.mp hsum).resolve_left hcard

lemma pair_g₀ : (pair (coefficients χ)).g₀ =
    ∑ p : (Fin χ.period × Fin χ.period) × Fin 2, coefficients χ p.1 *
      (parityPair (p.1.1 : ℕ) (p.1.2 : ℕ) χ.period (Nat.cast_pos.mpr (NeZero.pos χ.period)) p.2).ε *
      (parityPair (p.1.1 : ℕ) (p.1.2 : ℕ) χ.period (Nat.cast_pos.mpr (NeZero.pos χ.period)) p.2).g₀ := by
  simp [pair, finitePair]

lemma g₀_eq_zero (hχ : χ.residue ≠ 1) : (pair (coefficients χ)).g₀ = 0 := by
  rw [pair_g₀]
  -- the ε and g₀ of every component are the same constants
  have hε : ∀ p : (Fin χ.period × Fin χ.period) × Fin 2,
      (parityPair (p.1.1 : ℕ) (p.1.2 : ℕ) χ.period (Nat.cast_pos.mpr (NeZero.pos χ.period)) p.2).ε *
      (parityPair (p.1.1 : ℕ) (p.1.2 : ℕ) χ.period (Nat.cast_pos.mpr (NeZero.pos χ.period)) p.2).g₀ =
      (1 * (((χ.period : ℝ) ^ 2) ^ (-(1 / 2 : ℝ)) : ℝ)) * (1 * ((3 * (χ.period : ℝ) ^ 2) ^ (-(1 / 2 : ℝ)) : ℝ)) *
        (1 * 1) := fun _ => rfl
  simp_rw [mul_assoc, hε, ← mul_assoc, ← Finset.sum_mul]
  rw [Fintype.sum_prod_type]
  simp only [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul]
  rw [← Finset.mul_sum, sum_coefficients_eq_zero χ hχ]
  simp

/-- Holomorphy at `s = 1` for every nontrivial character. -/
theorem differentiableAt_one (hχ : χ.residue ≠ 1) : DifferentiableAt ℂ (LFunction χ) 1 :=
  StatementChecks.Hecke.differentiableAt_LFunction_one χ (g₀_eq_zero χ hχ)

/-- For every nontrivial character the defined L-function is entire. -/
theorem differentiable_of_ne_one (hχ : χ.residue ≠ 1) : Differentiable ℂ (LFunction χ) := by
  intro s
  by_cases h0 : s = 0
  · subst h0; exact differentiableAt_zero χ (modulus_ne_top χ hχ)
  by_cases h1 : s = 1
  · subst h1; exact differentiableAt_one χ hχ
  exact StatementChecks.Hecke.differentiableAt_LFunction χ h0 h1

/-! ### Independence of the auxiliary `period` -/

/-- The same character (modulus and residue) with a different choice of `period`. -/
def withPeriod (P : ℕ) (hP : 0 < P) (hPm : (P : O) ∈ χ.modulus) : Character :=
  { χ with period := P, period_pos := hP, period_mem := hPm }

/-- For `re s > 1` the value does not depend on `period`: the lattice series has no period in it. -/
theorem period_indep_of_one_lt_re (P : ℕ) (hP : 0 < P) (hPm : (P : O) ∈ χ.modulus) {s : ℂ}
    (hs : 1 < s.re) : LFunction (withPeriod χ P hP hPm) s = LFunction χ s :=
  (LFunction_hasSum (withPeriod χ P hP hPm) hs).unique (LFunction_hasSum χ hs)

/-- And on all of `ℂ ∖ {0, 1}`, by the identity theorem (both sides are holomorphic there and agree on
`re s > 1`). -/
theorem period_indep (P : ℕ) (hP : 0 < P) (hPm : (P : O) ∈ χ.modulus) {s : ℂ} (h0 : s ≠ 0)
    (h1 : s ≠ 1) : LFunction (withPeriod χ P hP hPm) s = LFunction χ s := by
  set U : Set ℂ := ({0, 1} : Set ℂ)ᶜ with hU
  have hUo : IsOpen U := (Set.Finite.isClosed (Set.toFinite _)).isOpen_compl
  have hdiff : ∀ χ' : Character, DifferentiableOn ℂ (LFunction χ') U := by
    intro χ' z hz
    simp only [hU, Set.mem_compl_iff, Set.mem_insert_iff, Set.mem_singleton_iff, not_or] at hz
    exact (StatementChecks.Hecke.differentiableAt_LFunction χ' hz.1 hz.2).differentiableWithinAt
  have hconn : IsPreconnected U :=
    ((Set.toFinite ({0, 1} : Set ℂ)).countable.isConnected_compl_of_one_lt_rank
      (by rw [Complex.rank_real_complex]; norm_num)).isPreconnected
  have h2 : (2 : ℂ) ∈ U := by simp [hU]
  have hev : LFunction (withPeriod χ P hP hPm) =ᶠ[nhds (2 : ℂ)] LFunction χ := by
    have hopen : IsOpen {z : ℂ | 1 < z.re} := isOpen_lt continuous_const Complex.continuous_re
    filter_upwards [hopen.mem_nhds (by norm_num : (1 : ℝ) < (2 : ℂ).re)] with z hz
    exact period_indep_of_one_lt_re χ P hP hPm hz
  have := ((hdiff _).analyticOnNhd hUo).eqOn_of_preconnected_of_eventuallyEq
    ((hdiff χ).analyticOnNhd hUo) hconn h2 hev
  exact this (by simp [hU, h0, h1])

end StatementChecks.HeckeHolo

#print axioms StatementChecks.HeckeHolo.residue_eq_one_of_top
#print axioms StatementChecks.HeckeHolo.f₀_eq_zero
#print axioms StatementChecks.HeckeHolo.differentiableAt_zero
#print axioms StatementChecks.HeckeHolo.trivialTop_at_zero
#print axioms StatementChecks.HeckeHolo.coord_surj
#print axioms StatementChecks.HeckeHolo.sum_coefficients_eq_zero
#print axioms StatementChecks.HeckeHolo.g₀_eq_zero
#print axioms StatementChecks.HeckeHolo.differentiableAt_one
#print axioms StatementChecks.HeckeHolo.differentiable_of_ne_one
#print axioms StatementChecks.HeckeHolo.period_indep_of_one_lt_re
#print axioms StatementChecks.HeckeHolo.period_indep
