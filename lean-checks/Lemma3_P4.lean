import Mathlib

open MvPolynomial Pointwise

namespace Lemma3

noncomputable section

/-- An integer vector as a real vector. -/
def zR (m : Fin 4 → ℤ) : Fin 4 → ℝ := fun i => (m i : ℝ)

/-- An integer vector as a complex vector. -/
def zC (m : Fin 4 → ℤ) : Fin 4 → ℂ := fun i => (m i : ℂ)

/-- A point of `E_N = {0,…,N−1}⁴` as an integer vector. -/
def emb {N : ℕ} (n : Fin 4 → Fin N) : Fin 4 → ℤ := fun i => ((n i : ℕ) : ℤ)

/-- Squared Euclidean distance on `ℝ⁴`. -/
def sqd (x y : Fin 4 → ℝ) : ℝ := dotProduct (x - y) (x - y)

/-- `𝒫_t`: polynomials in `z₁, z₂, z₃` with `deg_{z_j} B ≤ t_j`. -/
def Pt (t : Fin 3 → ℤ) : Set (MvPolynomial (Fin 3) ℂ) :=
  {B | ∀ j, (B.degreeOf j : ℤ) ≤ t j}

/-- The polynomial of a linear functional on `ℂ³`. -/
def p4_linP (ψ : (Fin 3 → ℂ) →ₗ[ℂ] ℂ) : MvPolynomial (Fin 3) ℂ :=
  ∑ j, C (ψ (fun l => if j = l then 1 else 0)) * X j

theorem p4_eval_linP (ψ : (Fin 3 → ℂ) →ₗ[ℂ] ℂ) (z : Fin 3 → ℂ) :
    eval z (p4_linP ψ) = ψ z := by
  rw [LinearMap.pi_apply_eq_sum_univ ψ z]
  simp only [p4_linP, map_sum, map_mul, eval_C, eval_X, smul_eq_mul]
  refine Finset.sum_congr rfl fun j _ => ?_
  ring

theorem p4_deg_linP (ψ : (Fin 3 → ℂ) →ₗ[ℂ] ℂ) : (p4_linP ψ).totalDegree ≤ 1 := by
  apply totalDegree_finsetSum_le
  intro j _
  refine (totalDegree_mul _ _).trans ?_
  rw [totalDegree_C, totalDegree_X]

/-- The linear functional `x ↦ ∑ r_j x_j`. -/
def p4_rL (r : Fin 4 → ℤ) : (Fin 4 → ℂ) →ₗ[ℂ] ℂ :=
  ∑ j, (r j : ℂ) • LinearMap.proj j

theorem p4_rL_apply (r : Fin 4 → ℤ) (x : Fin 4 → ℂ) :
    p4_rL r x = ∑ j, (r j : ℂ) * x j := by
  simp [p4_rL]

/-- Steps 13–14. `A` restricted to `ℋ = {r·v = k}` is an affine bijection (`r·c ≠ 0`), so
there is a Lagrange polynomial `Q` of total degree ≤ `3(N−1)` equal to 1 at `Au` and 0 at
`An` for the other `n ∈ E_N ∩ ℋ` in `T`. -/
theorem exists_lagrange (A : (Fin 4 → ℂ) →ₗ[ℂ] (Fin 3 → ℂ)) (hA : Function.Surjective A)
    (c : Fin 4 → ℂ) (hker : LinearMap.ker A = Submodule.span ℂ {c}) (r : Fin 4 → ℤ)
    (hrc : ∑ i, (r i : ℂ) * c i ≠ 0) (k : ℤ) (N : ℕ) (T : Set (Fin 4 → Fin N))
    (hT : ∀ n ∈ T, dotProduct r (emb n) = k) (u : Fin 4 → Fin N) (hu : u ∈ T) :
    ∃ Q : MvPolynomial (Fin 3) ℂ, Q.totalDegree ≤ 3 * (N - 1) ∧
      eval (A (zC (emb u))) Q = 1 ∧ ∀ n ∈ T, n ≠ u → eval (A (zC (emb n))) Q = 0 := by
  classical
  -- `r ≠ 0`, pick `i₀` with `r i₀ ≠ 0`.
  have hr : ∃ i₀, r i₀ ≠ 0 := by
    by_contra h
    push Not at h
    exact hrc (by simp [h])
  obtain ⟨i₀, hi₀⟩ := hr
  set s : ℂ := ∑ i, (r i : ℂ) * c i with hs
  obtain ⟨g, hg⟩ := A.exists_rightInverse_of_surjective (LinearMap.range_eq_top.2 hA)
  have hAg : ∀ z, A (g z) = z := fun z => by
    simpa using LinearMap.congr_fun hg z
  -- The affine functionals recovering the coordinates on `ℋ`.
  let ψ : Fin 4 → (Fin 3 → ℂ) →ₗ[ℂ] ℂ := fun i =>
    (LinearMap.proj i ∘ₗ g) - (c i / s) • (p4_rL r ∘ₗ g)
  let lam : Fin 4 → MvPolynomial (Fin 3) ℂ := fun i =>
    p4_linP (ψ i) + C (c i * (k : ℂ) / s)
  have hlam_deg : ∀ i, (lam i).totalDegree ≤ 1 := fun i =>
    (totalDegree_add _ _).trans (by rw [totalDegree_C]; simpa using p4_deg_linP (ψ i))
  have hlam_eval : ∀ x : Fin 4 → ℂ, ∑ j, (r j : ℂ) * x j = k →
      ∀ i, eval (A x) (lam i) = x i := by
    intro x hx i
    have hw : x - g (A x) ∈ LinearMap.ker A := by
      rw [LinearMap.mem_ker, map_sub, hAg, sub_self]
    rw [hker, Submodule.mem_span_singleton] at hw
    obtain ⟨t, ht⟩ := hw
    have hx' : x = g (A x) + t • c := by rw [ht]; abel
    have hrx : p4_rL r (g (A x)) = k - t * s := by
      have h1 : p4_rL r x = k := by rw [p4_rL_apply, hx]
      rw [hx', map_add, map_smul, smul_eq_mul, p4_rL_apply r c, ← hs] at h1
      linear_combination h1
    have hxi : x i = g (A x) i + t * c i := by
      conv_lhs => rw [hx']
      simp
    simp only [lam, eval_add, eval_C, p4_eval_linP, ψ, LinearMap.sub_apply,
      LinearMap.smul_apply, LinearMap.comp_apply, LinearMap.proj_apply, smul_eq_mul, hrx, hxi]
    field_simp
    ring
  have hTC : ∀ n ∈ T, ∑ j, (r j : ℂ) * zC (emb n) j = k := by
    intro n hn
    have := hT n hn
    simp only [dotProduct] at this
    simp only [zC]
    exact_mod_cast this
  have hzC : ∀ (n : Fin 4 → Fin N) i, zC (emb n) i = ((n i : ℕ) : ℂ) := by
    intro n i; simp [zC, emb]
  let I : Finset (Fin 4) := Finset.univ.erase i₀
  let fac : Fin 4 → ℕ → MvPolynomial (Fin 3) ℂ := fun i a =>
    (lam i - C (a : ℂ)) * C ((((u i : ℕ) : ℂ) - a)⁻¹)
  refine ⟨∏ i ∈ I, ∏ a ∈ (Finset.range N).erase (u i : ℕ), fac i a, ?_, ?_, ?_⟩
  · -- degree bound
    refine (totalDegree_finsetProd _ _).trans ?_
    have hI : I.card = 3 := by simp [I]
    have : ∀ i ∈ I, (∏ a ∈ (Finset.range N).erase (u i : ℕ), fac i a).totalDegree ≤ N - 1 := by
      intro i _
      refine (totalDegree_finsetProd _ _).trans ?_
      have hcard : ((Finset.range N).erase (u i : ℕ)).card = N - 1 := by
        rw [Finset.card_erase_of_mem (by simp), Finset.card_range]
      calc ∑ a ∈ (Finset.range N).erase (u i : ℕ), (fac i a).totalDegree
          ≤ ∑ _a ∈ (Finset.range N).erase (u i : ℕ), 1 := by
            refine Finset.sum_le_sum fun a _ => ?_
            refine (totalDegree_mul _ _).trans ?_
            rw [totalDegree_C, add_zero]
            exact (totalDegree_sub_C_le _ _).trans (hlam_deg i)
        _ = N - 1 := by simp [hcard]
    calc ∑ i ∈ I, (∏ a ∈ (Finset.range N).erase (u i : ℕ), fac i a).totalDegree
        ≤ ∑ _i ∈ I, (N - 1) := Finset.sum_le_sum this
      _ = 3 * (N - 1) := by simp [hI]
  · -- value 1 at `Au`
    rw [map_prod]
    refine Finset.prod_eq_one fun i _ => ?_
    rw [map_prod]
    refine Finset.prod_eq_one fun a ha => ?_
    have hne : ((u i : ℕ) : ℂ) - a ≠ 0 := by
      rw [sub_ne_zero, Ne, Nat.cast_inj]
      exact fun h => (Finset.ne_of_mem_erase ha) h.symm
    simp only [fac, eval_mul, eval_sub, eval_C, hlam_eval _ (hTC u hu), hzC]
    exact mul_inv_cancel₀ hne
  · -- value 0 at the other points
    intro n hn hnu
    have hex : ∃ i ∈ I, n i ≠ u i := by
      by_contra h
      push Not at h
      apply hnu
      have hoff : ∀ i, i ≠ i₀ → n i = u i := fun i hi => h i (by simp [I, hi])
      have h0 : n i₀ = u i₀ := by
        have e1 := hT n hn
        have e2 := hT u hu
        rw [← e2] at e1
        simp only [dotProduct, emb] at e1
        rw [Fin.sum_univ_four, Fin.sum_univ_four] at e1
        have key : r i₀ * ((n i₀ : ℕ) : ℤ) = r i₀ * ((u i₀ : ℕ) : ℤ) := by
          fin_cases i₀ <;> simp_all
        have := mul_left_cancel₀ hi₀ key
        exact Fin.ext (by exact_mod_cast this)
      funext i
      by_cases hi : i = i₀
      · subst hi; exact h0
      · exact hoff i hi
    obtain ⟨i, hiI, hni⟩ := hex
    rw [map_prod]
    refine Finset.prod_eq_zero hiI ?_
    rw [map_prod]
    refine Finset.prod_eq_zero (i := (n i : ℕ)) ?_ ?_
    · simp only [Finset.mem_erase, Finset.mem_range]
      exact ⟨fun h => hni (Fin.ext h), (n i).isLt⟩
    · simp only [fac, eval_mul, eval_sub, eval_C, hlam_eval _ (hTC n hn), hzC, sub_self,
        zero_mul]

end

end Lemma3

#print axioms Lemma3.exists_lagrange
