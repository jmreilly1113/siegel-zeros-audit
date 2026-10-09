import Mathlib

/-!
# Corollary 4 (`cor:rectangle`) of "Uniform exclusion of Landau–Siegel zeros"

Paper: refs/siegel-paper.tex lines 410–432. Derived from Lemma 3 (`interpolation`),
which is proved in lean-checks/Lemma3.lean; here it is a stub replaced on merge.
-/

open MvPolynomial Pointwise

namespace Lemma3

noncomputable section

/-- `𝒫_t`: polynomials in `z₁, z₂, z₃` with `deg_{z_j} B ≤ t_j`. -/
def Pt (t : Fin 3 → ℤ) : Set (MvPolynomial (Fin 3) ℂ) :=
  {B | ∀ j, (B.degreeOf j : ℤ) ≤ t j}


/-- **Lemma 3** (`lem:interpolation`, tex lines 252–267). -/
theorem interpolation
    (A : (Fin 4 → ℂ) →ₗ[ℂ] (Fin 3 → ℂ)) (hA : Function.Surjective A)
    (c : Fin 4 → ℂ) (hker : LinearMap.ker A = Submodule.span ℂ {c})
    (hc : LinearIndependent ℚ c)
    (N : ℕ) (hN : 1 ≤ N) (t : Fin 3 → ℤ)
    (ht : ∀ j, 3 * ((N : ℤ) - 1) ≤ t j)
    (hbudget : (4 * (N : ℤ) - 3) ^ 4 < ∏ j, (t j - 3 * ((N : ℤ) - 1) + 1)) :
    Function.Surjective
      (fun B : Pt t => fun n : Fin 4 → Fin N =>
        eval (A (fun i => ((n i : ℕ) : ℂ))) (B : MvPolynomial (Fin 3) ℂ)) := by sorry

/-- `(H^{1/3})^2 = H^{2/3}` and friends. -/
lemma cor4_rpow_nat (x : ℝ) (hx : 0 ≤ x) (k : ℕ) :
    (x ^ (1 / 3 : ℝ)) ^ k = x ^ ((k : ℝ) / 3) := by
  rw [← Real.rpow_natCast, ← Real.rpow_mul hx]; ring_nf

lemma cor4_cube (x : ℝ) (hx : 0 ≤ x) : (x ^ (1 / 3 : ℝ)) ^ 3 = x := by
  rw [cor4_rpow_nat x hx 3]; norm_num

/-- The real-number estimates of the corollary's proof. -/
lemma cor4_real (H N : ℕ) (hH : 1 ≤ H) (hHN : H ≤ N) :
    let T0 := 32 * (H : ℝ) ^ (2 / 3 : ℝ) * (N : ℝ) ^ (4 / 3 : ℝ)
    let T1 := 32 * (H : ℝ) ^ (-(1 / 3 : ℝ)) * (N : ℝ) ^ (4 / 3 : ℝ)
    32 * (N : ℝ) ≤ T0 ∧ 32 * (N : ℝ) ≤ T1 ∧ T0 * T1 * T1 = 32 ^ 3 * (N : ℝ) ^ 4 := by
  intro T0 T1
  have hH0 : (0 : ℝ) ≤ H := by positivity
  have hN0 : (0 : ℝ) ≤ N := by positivity
  set a := (H : ℝ) ^ (1 / 3 : ℝ) with ha
  set b := (N : ℝ) ^ (1 / 3 : ℝ) with hb
  have ha1 : 1 ≤ a := Real.one_le_rpow (by exact_mod_cast hH) (by norm_num)
  have hab : a ≤ b := Real.rpow_le_rpow hH0 (by exact_mod_cast hHN) (by norm_num)
  have hb1 : 1 ≤ b := ha1.trans hab
  have hA2 : (H : ℝ) ^ (2 / 3 : ℝ) = a ^ 2 := by
    rw [ha, cor4_rpow_nat _ hH0 2]; norm_num
  have hAm : (H : ℝ) ^ (-(1 / 3 : ℝ)) = a⁻¹ := by rw [Real.rpow_neg hH0]
  have hB4 : (N : ℝ) ^ (4 / 3 : ℝ) = b ^ 4 := by
    rw [hb, cor4_rpow_nat _ hN0 4]; norm_num
  have hN3 : (N : ℝ) = b ^ 3 := (cor4_cube _ hN0).symm
  have hT0 : T0 = 32 * a ^ 2 * b ^ 4 := by simp only [T0, hA2, hB4]
  have hT1 : T1 = 32 * a⁻¹ * b ^ 4 := by simp only [T1, hAm, hB4]
  have ha0 : 0 < a := by linarith
  refine ⟨?_, ?_, ?_⟩
  · rw [hT0, hN3]
    have : b ^ 3 ≤ a ^ 2 * b ^ 4 := by
      have h1 : 1 ≤ a ^ 2 := one_le_pow₀ ha1
      have h2 : b ^ 3 ≤ b ^ 4 := pow_le_pow_right₀ hb1 (by norm_num)
      nlinarith [pow_pos (by linarith : (0:ℝ) < b) 4]
    nlinarith
  · rw [hT1, hN3]
    have : b ^ 3 ≤ a⁻¹ * b ^ 4 := by
      rw [le_inv_mul_iff₀ ha0]
      have : a * b ^ 3 ≤ b * b ^ 3 :=
        mul_le_mul_of_nonneg_right hab (by positivity)
      nlinarith
    nlinarith
  · rw [hT0, hT1, hN3]
    field_simp

/-- The box `t_j = ⌊T_j⌋` satisfies the hypotheses (`eq:budget`) of Lemma 3. -/
lemma cor4_budget (N : ℕ) (hN : 1 ≤ N) (T : Fin 3 → ℝ) (hT : ∀ j, 32 * (N : ℝ) ≤ T j)
    (hprod : T 0 * T 1 * T 2 = 32 ^ 3 * (N : ℝ) ^ 4) :
    (∀ j, 3 * ((N : ℤ) - 1) ≤ ⌊T j⌋) ∧
      (4 * (N : ℤ) - 3) ^ 4 < ∏ j, (⌊T j⌋ - 3 * ((N : ℤ) - 1) + 1) := by
  have hN1 : (1 : ℝ) ≤ N := by exact_mod_cast hN
  refine ⟨fun j => ?_, ?_⟩
  · rw [Int.le_floor]; push_cast; linarith [hT j]
  · rw [← @Int.cast_lt ℝ]
    push_cast
    rw [Fin.prod_univ_three]
    have hx : ∀ j, T j / 2 < (⌊T j⌋ : ℝ) - 3 * ((N : ℝ) - 1) + 1 := fun j => by
      have := Int.lt_floor_add_one (T j)
      linarith [hT j]
    have hpos : ∀ j, 0 ≤ T j / 2 := fun j => by linarith [hT j]
    have hp : T 0 / 2 * (T 1 / 2) * (T 2 / 2) <
        ((⌊T 0⌋ : ℝ) - 3 * ((N : ℝ) - 1) + 1) * ((⌊T 1⌋ : ℝ) - 3 * ((N : ℝ) - 1) + 1) *
          ((⌊T 2⌋ : ℝ) - 3 * ((N : ℝ) - 1) + 1) :=
      mul_lt_mul'' (mul_lt_mul'' (hx 0) (hx 1) (hpos 0) (hpos 1)) (hx 2)
        (mul_nonneg (hpos 0) (hpos 1)) (hpos 2)
    have he : T 0 / 2 * (T 1 / 2) * (T 2 / 2) = (8 * (N : ℝ)) ^ 4 := by
      have : T 0 / 2 * (T 1 / 2) * (T 2 / 2) = (T 0 * T 1 * T 2) / 8 := by ring
      rw [this, hprod]; ring
    have hl : (4 * (N : ℝ) - 3) ^ 4 < (8 * (N : ℝ)) ^ 4 :=
      pow_lt_pow_left₀ (by linarith) (by linarith) (by norm_num)
    linarith

/-- **Corollary 4** (`cor:rectangle`, tex lines 410–420). -/
theorem rectangle
    (A : (Fin 4 → ℂ) →ₗ[ℂ] (Fin 3 → ℂ)) (hA : Function.Surjective A)
    (c : Fin 4 → ℂ) (hker : LinearMap.ker A = Submodule.span ℂ {c})
    (hc : LinearIndependent ℚ c)
    (H N : ℕ) (hH : 1 ≤ H) (hHN : H ≤ N) :
    Submodule.span ℂ
      ((fun α : Fin 3 → ℕ => fun n : Fin 4 → Fin N =>
          A (fun i => ((n i : ℕ) : ℂ)) 0 ^ α 0 * A (fun i => ((n i : ℕ) : ℂ)) 1 ^ α 1 *
            A (fun i => ((n i : ℕ) : ℂ)) 2 ^ α 2) ''
        {α : Fin 3 → ℕ |
          (α 0 : ℝ) ≤ 32 * (H : ℝ) ^ (2 / 3 : ℝ) * (N : ℝ) ^ (4 / 3 : ℝ) ∧
          (α 1 : ℝ) ≤ 32 * (H : ℝ) ^ (-(1 / 3 : ℝ)) * (N : ℝ) ^ (4 / 3 : ℝ) ∧
          (α 2 : ℝ) ≤ 32 * (H : ℝ) ^ (-(1 / 3 : ℝ)) * (N : ℝ) ^ (4 / 3 : ℝ)}) = ⊤ := by
  classical
  have hN : 1 ≤ N := le_trans hH hHN
  obtain ⟨h0, h1, hprod⟩ := cor4_real H N hH hHN
  set T : Fin 3 → ℝ := ![32 * (H : ℝ) ^ (2 / 3 : ℝ) * (N : ℝ) ^ (4 / 3 : ℝ),
    32 * (H : ℝ) ^ (-(1 / 3 : ℝ)) * (N : ℝ) ^ (4 / 3 : ℝ),
    32 * (H : ℝ) ^ (-(1 / 3 : ℝ)) * (N : ℝ) ^ (4 / 3 : ℝ)] with hTdef
  have hT : ∀ j, 32 * (N : ℝ) ≤ T j := by
    intro j; fin_cases j
    · exact h0
    · exact h1
    · exact h1
  obtain ⟨ht, hb⟩ := cor4_budget N hN T hT hprod
  have hsurj := interpolation A hA c hker hc N hN (fun j => ⌊T j⌋) ht hb
  rw [eq_top_iff]
  rintro w -
  obtain ⟨⟨B, hB⟩, hBw⟩ := hsurj w
  rw [← hBw]
  have hsum : (fun n : Fin 4 → Fin N => eval (A (fun i => ((n i : ℕ) : ℂ))) B) =
      ∑ d ∈ B.support, B.coeff d • (fun n : Fin 4 → Fin N =>
        A (fun i => ((n i : ℕ) : ℂ)) 0 ^ d 0 * A (fun i => ((n i : ℕ) : ℂ)) 1 ^ d 1 *
          A (fun i => ((n i : ℕ) : ℂ)) 2 ^ d 2) := by
    funext n
    rw [eval_eq', Finset.sum_apply]
    simp only [Pi.smul_apply, smul_eq_mul, Fin.prod_univ_three, mul_assoc]
  simp only
  rw [hsum]
  refine Submodule.sum_mem _ fun d hd => Submodule.smul_mem _ _ (Submodule.subset_span
    ⟨fun i => d i, ?_, rfl⟩)
  have hdj : ∀ j, (d j : ℝ) ≤ T j := fun j => by
    have h1 := monomial_le_degreeOf j hd
    have h2 := hB j
    have : ((d j : ℕ) : ℤ) ≤ ⌊T j⌋ := le_trans (by exact_mod_cast h1) h2
    exact_mod_cast (Int.le_floor.1 this)
  exact ⟨hdj 0, hdj 1, hdj 2⟩

end

end Lemma3

#print axioms Lemma3.rectangle
