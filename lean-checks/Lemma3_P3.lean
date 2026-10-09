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

/-- The `ℚ`-linear functional `v ↦ ∑ h i * v i` on `ℚ⁴`, with values in `ℝ`. -/
def p3_g (h : Fin 4 → ℝ) : (Fin 4 → ℚ) →ₗ[ℚ] ℝ where
  toFun v := ∑ i, h i * (v i : ℝ)
  map_add' v w := by
    simp only [Pi.add_apply, Rat.cast_add, mul_add, Finset.sum_add_distrib]
  map_smul' a v := by
    simp only [Pi.smul_apply, smul_eq_mul, Rat.cast_mul, RingHom.id_apply, Rat.smul_def,
      Finset.mul_sum]
    refine Finset.sum_congr rfl fun i _ => ?_
    ring

theorem p3_g_apply (h : Fin 4 → ℝ) (v : Fin 4 → ℚ) : p3_g h v = ∑ i, h i * (v i : ℝ) := rfl

/-- Clearing denominators of a rational vector. -/
theorem p3_clear (w : Fin 4 → ℚ) :
    ∃ (L : ℕ) (r : Fin 4 → ℤ), L ≠ 0 ∧ ∀ i, (r i : ℚ) = w i * L := by
  classical
  refine ⟨∏ i, (w i).den, ?_⟩
  have hex : ∀ i, ∃ z : ℤ, (z : ℚ) = w i * ((∏ j, (w j).den : ℕ) : ℚ) := by
    intro i
    obtain ⟨M, hM⟩ := Finset.dvd_prod_of_mem (fun j => (w j).den) (Finset.mem_univ i)
    refine ⟨(w i).num * M, ?_⟩
    rw [hM]
    push_cast
    rw [← mul_assoc, Rat.mul_den_eq_num]
  choose r hr using hex
  exact ⟨r, Finset.prod_ne_zero_iff.2 fun i _ => (w i).den_nz, hr⟩

/-- Step 12. Integer points on a real hyperplane `h· = const` (`h ≠ 0`) lie on an integer
hyperplane `r· = k`, `0 ≠ r ∈ ℤ⁴`. -/
theorem exists_int_hyperplane (T : Set (Fin 4 → ℤ)) (h : Fin 4 → ℝ) (hh : h ≠ 0)
    (hT : ∀ s ∈ T, ∀ s' ∈ T, dotProduct h (zR s) = dotProduct h (zR s')) :
    ∃ r : Fin 4 → ℤ, r ≠ 0 ∧ ∃ k : ℤ, ∀ s ∈ T, dotProduct r s = k := by
  classical
  rcases T.eq_empty_or_nonempty with hTe | ⟨s0, hs0⟩
  · refine ⟨fun _ => 1, fun h0 => by simpa using congrFun h0 0, 0, ?_⟩
    intro s hs
    simp [hTe] at hs
  set D : Set (Fin 4 → ℚ) :=
    {v | ∃ s ∈ T, v = fun i => (((s i - s0 i : ℤ)) : ℚ)} with hDdef
  set V : Submodule ℚ (Fin 4 → ℚ) := Submodule.span ℚ D with hVdef
  have hDker : D ⊆ LinearMap.ker (p3_g h) := by
    rintro _ ⟨s, hs, rfl⟩
    rw [SetLike.mem_coe, LinearMap.mem_ker, p3_g_apply]
    have := hT s hs s0 hs0
    simp only [dotProduct, zR] at this
    simp only [Int.cast_sub, Rat.cast_sub, Rat.cast_intCast, mul_sub, Finset.sum_sub_distrib]
    linarith
  have hVlt : V < ⊤ := by
    refine lt_top_iff_ne_top.2 fun hV => hh ?_
    have hle : V ≤ LinearMap.ker (p3_g h) := Submodule.span_le.2 hDker
    rw [hV] at hle
    funext j
    have hj := hle (Submodule.mem_top (x := Pi.single j (1 : ℚ)))
    rw [LinearMap.mem_ker, p3_g_apply] at hj
    simpa [Pi.single_apply, apply_ite, mul_ite, Finset.sum_ite_eq'] using hj
  obtain ⟨f, hf0, hVf⟩ := V.exists_le_ker_of_lt_top hVlt
  set w : Fin 4 → ℚ := fun i => f (fun j => if i = j then 1 else 0) with hwdef
  have hfw : ∀ x, f x = ∑ i, x i * w i := by
    intro x
    rw [f.pi_apply_eq_sum_univ x]
    rfl
  obtain ⟨L, r, hL, hr⟩ := p3_clear w
  refine ⟨r, ?_, dotProduct r s0, ?_⟩
  · intro hr0
    apply hf0
    refine LinearMap.ext fun x => ?_
    rw [hfw x, LinearMap.zero_apply]
    refine Finset.sum_eq_zero fun i _ => ?_
    have := hr i
    rw [hr0, Pi.zero_apply, Int.cast_zero] at this
    have hw : w i = 0 := by
      rcases mul_eq_zero.1 this.symm with h1 | h1
      · exact h1
      · exact absurd (by exact_mod_cast h1) hL
    rw [hw, mul_zero]
  · intro s hs
    have hd : (fun i => (((s i - s0 i : ℤ)) : ℚ)) ∈ LinearMap.ker f :=
      hVf (Submodule.subset_span ⟨s, hs, rfl⟩)
    rw [LinearMap.mem_ker, hfw] at hd
    have key : ((dotProduct r s - dotProduct r s0 : ℤ) : ℚ) = 0 := by
      have e : ((dotProduct r s - dotProduct r s0 : ℤ) : ℚ) =
          (L : ℚ) * ∑ i, (((s i - s0 i : ℤ)) : ℚ) * w i := by
        simp only [dotProduct, Int.cast_sub, Int.cast_sum, Int.cast_mul, hr, Finset.mul_sum,
          ← Finset.sum_sub_distrib]
        refine Finset.sum_congr rfl fun i _ => ?_
        ring
      rw [e, hd, mul_zero]
    have : dotProduct r s - dotProduct r s0 = 0 := by exact_mod_cast key
    linarith

/-- Step 12. Rational independence of the coordinates of `c` gives `r·c ≠ 0`. -/
theorem int_comb_ne_zero (c : Fin 4 → ℂ) (hc : LinearIndependent ℚ c) (r : Fin 4 → ℤ)
    (hr : r ≠ 0) : ∑ i, (r i : ℂ) * c i ≠ 0 := by
  intro hsum
  apply hr
  have h0 : ∑ i, ((r i : ℚ)) • c i = 0 := by
    simpa only [Rat.smul_def, Rat.cast_intCast] using hsum
  funext i
  have := Fintype.linearIndependent_iff.1 hc (fun i => (r i : ℚ)) h0 i
  exact_mod_cast this

end

end Lemma3

#print axioms Lemma3.exists_int_hyperplane
#print axioms Lemma3.int_comb_ne_zero
