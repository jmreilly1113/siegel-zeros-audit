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

/-! ## Piece 5 helpers -/

/-- `𝒫_t` as a submodule when `t ≥ 0`. -/
def p5_PtSub (t : Fin 3 → ℤ) (ht0 : ∀ j, 0 ≤ t j) :
    Submodule ℂ (MvPolynomial (Fin 3) ℂ) where
  carrier := Pt t
  add_mem' := by
    intro a b ha hb
    simp only [Pt, Set.mem_ofPred_eq] at *
    intro j
    have h := degreeOf_add_le j a b
    have h' : ((a + b).degreeOf j : ℤ) ≤ max (a.degreeOf j : ℤ) (b.degreeOf j : ℤ) := by
      exact_mod_cast h
    exact h'.trans (max_le (ha j) (hb j))
  zero_mem' := by
    simp only [Pt, Set.mem_ofPred_eq]
    intro j
    simp [ht0 j]
  smul_mem' := by
    intro c a ha
    simp only [Pt, Set.mem_ofPred_eq] at *
    intro j
    rw [smul_eq_C_mul]
    exact le_trans (by exact_mod_cast degreeOf_C_mul_le a j c) (ha j)

theorem p5_eval_aeval {σ τ : Type*} (g : σ → MvPolynomial τ ℂ) (y : τ → ℂ)
    (p : MvPolynomial σ ℂ) :
    eval y (aeval g p) = eval (fun j => eval y (g j)) p := by
  induction p using MvPolynomial.induction_on with
  | C a => simp
  | add p q hp hq => rw [map_add, map_add, map_add, hp, hq]
  | mul_X p i hp => rw [map_mul, map_mul, map_mul, hp, aeval_X, eval_X]

/-! ## Piece 5 theorems -/

theorem exists_annihilator {ι : Type*} [Fintype ι] (t : Fin 3 → ℤ) (ht0 : ∀ j, 0 ≤ t j)
    (f : ι → Fin 3 → ℂ) (h : ¬ Function.Surjective
      (fun B : Pt t => fun n => eval (f n) (B : MvPolynomial (Fin 3) ℂ))) :
    ∃ v : ι → ℂ, v ≠ 0 ∧ ∀ B ∈ Pt t, ∑ n, v n * eval (f n) B = 0 := by
  classical
  let E : MvPolynomial (Fin 3) ℂ →ₗ[ℂ] (ι → ℂ) :=
    LinearMap.pi (fun n => (aeval (f n)).toLinearMap)
  have hE : ∀ B n, E B n = eval (f n) B := by
    intro B n
    simp [E, coe_aeval_eq_eval]
  let M : Submodule ℂ (ι → ℂ) := (p5_PtSub t ht0).map E
  have hM : M ≠ ⊤ := by
    intro hM
    apply h
    intro y
    have hy : y ∈ M := hM ▸ Submodule.mem_top
    obtain ⟨B, hB, hBy⟩ := Submodule.mem_map.1 hy
    refine ⟨⟨B, hB⟩, ?_⟩
    funext n
    rw [← hBy, hE]
  obtain ⟨φ, hφ0, hle⟩ := Submodule.exists_le_ker_of_lt_top M (lt_top_iff_ne_top.2 hM)
  refine ⟨fun n => φ (fun j => if n = j then 1 else 0), ?_, ?_⟩
  · intro hv
    apply hφ0
    refine LinearMap.ext fun x => ?_
    rw [LinearMap.pi_apply_eq_sum_univ φ x]
    simp only [LinearMap.zero_apply]
    apply Finset.sum_eq_zero
    intro i _
    have := congrFun hv i
    simp only [Pi.zero_apply] at this
    rw [this, smul_zero]
  · intro B hB
    have hmem : E B ∈ LinearMap.ker φ := hle (Submodule.mem_map_of_mem (p := p5_PtSub t ht0) hB)
    rw [LinearMap.mem_ker, LinearMap.pi_apply_eq_sum_univ φ] at hmem
    refine Eq.trans (Finset.sum_congr rfl (fun n _ => ?_)) hmem
    show _ * _ = _
    rw [hE, smul_eq_mul, mul_comm]

theorem four_hull_subset_cube (L : ℝ) (X : Set (Fin 4 → ℝ))
    (hX : ∀ x ∈ X, ∀ i, 0 ≤ x i ∧ x i ≤ L) :
    ∀ x ∈ (4 : ℝ) • convexHull ℝ X, ∀ i, 0 ≤ x i ∧ x i ≤ 4 * L := by
  intro x hx i
  obtain ⟨y, hy, rfl⟩ := hx
  have hbox : convexHull ℝ X ⊆ {y : Fin 4 → ℝ | ∀ i, 0 ≤ y i ∧ y i ≤ L} := by
    apply convexHull_min
    · intro z hz
      exact hX z hz
    · intro a ha b hb μ ν hμ hν hμν
      simp only [Set.mem_ofPred_eq] at ha hb ⊢
      intro i
      simp only [Pi.add_apply, Pi.smul_apply, smul_eq_mul]
      obtain ⟨a0, a1⟩ := ha i
      obtain ⟨b0, b1⟩ := hb i
      constructor <;> nlinarith
  obtain ⟨h0, h1⟩ := hbox hy i
  simp only [Pi.smul_apply, smul_eq_mul]
  constructor <;> linarith

theorem exists_vanishing (A : (Fin 4 → ℂ) →ₗ[ℂ] (Fin 3 → ℂ)) (b : Fin 3 → ℕ)
    (Z : Finset (Fin 4 → ℤ)) (hZ : Z.card < ∏ j, (b j + 1)) :
    ∃ R : MvPolynomial (Fin 3) ℂ, R ≠ 0 ∧ (∀ j, R.degreeOf j ≤ b j) ∧
      ∀ m ∈ Z, eval (A (zC m)) R = 0 := by
  classical
  set I := Fintype.piFinset (fun j : Fin 3 => Finset.range (b j + 1)) with hI
  let e : (Fin 3 → ℕ) → (Fin 3 →₀ ℕ) := fun s => Finsupp.equivFunOnFinite.symm s
  have he : Function.Injective e := Finsupp.equivFunOnFinite.symm.injective
  let M : Matrix Z I ℂ := fun m s => (e s.1).prod (fun i k => (A (zC m.1)) i ^ k)
  have hcard : Module.finrank ℂ (Z → ℂ) < Module.finrank ℂ (I → ℂ) := by
    simp only [Module.finrank_fintype_fun_eq_card, Fintype.card_coe, hI,
      Fintype.card_piFinset, Finset.card_range]
    exact hZ
  obtain ⟨c, hc, hc0⟩ := Submodule.exists_mem_ne_zero_of_ne_bot
    (LinearMap.ker_ne_bot_of_finrank_lt (f := M.mulVecLin) hcard)
  rw [LinearMap.mem_ker, Matrix.mulVecLin_apply] at hc
  obtain ⟨s0, hs0⟩ : ∃ s0, c s0 ≠ 0 := by
    by_contra hne
    push Not at hne
    exact hc0 (funext hne)
  have hcoeff : ∀ m, (∑ s : I, monomial (e s.1) (c s)).coeff m =
      ∑ s : I, if e s.1 = m then c s else 0 := by
    intro m
    rw [MvPolynomial.coeff_sum]
    simp only [MvPolynomial.coeff_monomial]
  refine ⟨∑ s : I, monomial (e s.1) (c s), ?_, ?_, ?_⟩
  · intro h0
    have h1 := hcoeff (e s0.1)
    rw [h0, AddMonoidAlgebra.coeff_zero, Finset.sum_eq_single s0] at h1
    · simp at h1
      exact hs0 h1.symm
    · intro s _ hs
      rw [if_neg]
      intro hes
      exact hs (Subtype.ext (he hes))
    · simp
  · intro j
    rw [degreeOf_le_iff]
    intro m hm
    rw [mem_support_iff, hcoeff] at hm
    obtain ⟨s, -, hs⟩ := Finset.exists_ne_zero_of_sum_ne_zero hm
    have hsm : e s.1 = m := by
      by_contra hne
      simp [hne] at hs
    have hsI : s.1 ∈ Fintype.piFinset (fun j : Fin 3 => Finset.range (b j + 1)) := s.2
    rw [Fintype.mem_piFinset] at hsI
    have := Finset.mem_range.1 (hsI j)
    rw [← hsm]
    have hk : (e s.1) j = s.1 j := by simp [e]
    omega
  · intro m hm
    have h1 := congrFun hc ⟨m, hm⟩
    simp only [Matrix.mulVec, dotProduct, Pi.zero_apply, M] at h1
    rw [map_sum, ← h1]
    refine Finset.sum_congr rfl (fun s _ => ?_)
    rw [eval_monomial, mul_comm]

theorem exists_lattice_nonvanishing (A : (Fin 4 → ℂ) →ₗ[ℂ] (Fin 3 → ℂ))
    (hA : Function.Surjective A) (R : MvPolynomial (Fin 3) ℂ) (hR : R ≠ 0) :
    ∃ m : Fin 4 → ℤ, eval (A (zC m)) R ≠ 0 := by
  classical
  let g : Fin 3 → MvPolynomial (Fin 4) ℂ :=
    fun j => ∑ i, C (A (fun k => if i = k then 1 else 0) j) * X i
  have hg : ∀ y, (fun j => eval y (g j)) = A y := by
    intro y
    funext j
    rw [LinearMap.pi_apply_eq_sum_univ A y]
    simp [g, Finset.sum_apply, mul_comm]
  have hP : ∀ y, eval y (aeval g R) = eval (A y) R := fun y => by
    rw [p5_eval_aeval, hg]
  by_contra hcon
  push Not at hcon
  apply hR
  have hP0 : aeval g R = 0 := by
    apply funext_set (fun _ => Set.range (fun n : ℤ => (n : ℂ)))
      (fun _ => Set.infinite_range_of_injective Int.cast_injective)
    intro x hx
    simp only [Set.mem_pi, Set.mem_univ, true_implies, Set.mem_range] at hx
    choose m hm using hx
    have hx' : x = zC m := by
      funext i
      simp [zC, hm]
    rw [hx', hP, hcon m, map_zero]
  apply MvPolynomial.funext
  intro z
  obtain ⟨y, rfl⟩ := hA z
  rw [← hP, hP0]
  simp

theorem exists_translate (R : MvPolynomial (Fin 3) ℂ) (w : Fin 3 → ℂ) :
    ∃ R' : MvPolynomial (Fin 3) ℂ, (∀ j, R'.degreeOf j ≤ R.degreeOf j) ∧
      ∀ z, eval z R' = eval (z + w) R := by
  classical
  refine ⟨aeval (fun j => X j + C (w j)) R, ?_, ?_⟩
  · intro j
    conv_lhs => rw [R.as_sum]
    rw [map_sum]
    refine Finset.sum_induction _
      (fun q : MvPolynomial (Fin 3) ℂ => degreeOf j q ≤ degreeOf j R) ?_ ?_ ?_
    · intro a b ha hb
      exact (degreeOf_add_le j a b).trans (max_le ha hb)
    · simp
    · intro s hs
      rw [aeval_monomial, algebraMap_eq, Finsupp.prod_fintype _ _ (by simp)]
      refine (degreeOf_C_mul_le _ _ _).trans ?_
      refine (degreeOf_prod_le _ _ _).trans ?_
      refine le_trans ?_ (monomial_le_degreeOf j hs)
      calc ∑ i, ((X i + C (w i) : MvPolynomial (Fin 3) ℂ) ^ s i).degreeOf j
          ≤ ∑ i, if i = j then s i else 0 := by
            apply Finset.sum_le_sum
            intro i _
            refine (degreeOf_pow_le _ _ _).trans ?_
            have hd : (X i + C (w i) : MvPolynomial (Fin 3) ℂ).degreeOf j ≤
                if i = j then 1 else 0 := by
              refine (degreeOf_add_le _ _ _).trans ?_
              rcases eq_or_ne i j with rfl | hij
              · simp [degreeOf_X, degreeOf_C]
              · simp [degreeOf_X, degreeOf_C, hij, hij.symm]
            rcases eq_or_ne i j with rfl | hij
            · simp only [ite_true] at hd ⊢
              nlinarith
            · simp only [hij, ite_false] at hd ⊢
              simp [Nat.le_zero.1 hd]
        _ = s j := by simp
  · intro z
    rw [p5_eval_aeval]
    have hzw : (fun j => eval z (X j + C (w j) : MvPolynomial (Fin 3) ℂ)) = z + w := by
      funext j
      simp
    rw [hzw]

end

end Lemma3

#print axioms Lemma3.exists_annihilator
#print axioms Lemma3.four_hull_subset_cube
#print axioms Lemma3.exists_vanishing
#print axioms Lemma3.exists_lattice_nonvanishing
#print axioms Lemma3.exists_translate
