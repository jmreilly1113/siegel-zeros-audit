import Mathlib
import OAI.NumberTheory.SiegelZeros.PaperLemma3.Lemma3
import OAI.NumberTheory.SiegelZeros.Structure.InvariantJetLinearMap

/-!
# Corollary 4 and the bridge to OAI's `actual_biquadratic_rectangle_span`, via the paper's Lemma 3

Copied from the Siegel-zero verification project, lean-checks/Lemma3Bridged.lean lines 989-1265
(proofs only). `Lemma3.actual_biquadratic_rectangle_span_via_lemma3` has exactly the type of
OAI's `actual_biquadratic_rectangle_span` (via `type_of%`) and is proved without OAI's
multiplicity estimate.
-/

open MvPolynomial Pointwise

namespace Lemma3

noncomputable section

/-! ## Corollary 4 from Lemma 3 (from lean-checks/Lemma3_Cor4.lean) -/

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

/-! ## Bridge to the OAI formalization (from lean-checks/Lemma3_Bridge.lean) -/

/-- Restriction to an injectively embedded set of columns and descent from `ℂ` to `K`:
if the `φ`-images of the rows `g i` (as columns indexed by `κ`) are the restrictions along
`ν` of rows `f i` spanning `E → ℂ`, then the rows `g i` span `κ → K`. -/
theorem bridge_descent {K κ ι E : Type*} [Field K] [Fintype κ] [DecidableEq κ]
    [DecidableEq E] (φ : K →+* ℂ) {g : ι → κ → K} {f : ι → E → ℂ} {S : Set ι}
    (ν : κ → E) (hν : Function.Injective ν)
    (hgf : ∀ i j, φ (g i j) = f i (ν j))
    (hf : Submodule.span ℂ (f '' S) = ⊤) :
    Submodule.span K (g '' S) = ⊤ := by
  by_contra hne
  obtain ⟨F, hF0, hFle⟩ :=
    Submodule.exists_le_ker_of_lt_top _ (lt_top_iff_ne_top.mpr hne)
  let lam : κ → K := fun j => F (fun k => if j = k then 1 else 0)
  have hFapp : ∀ w : κ → K, F w = ∑ j, w j * lam j := by
    intro w
    rw [LinearMap.pi_apply_eq_sum_univ F w]
    simp [lam, smul_eq_mul]
  obtain ⟨j0, hj0⟩ : ∃ j, lam j ≠ 0 := by
    by_contra h
    push Not at h
    exact hF0 (LinearMap.ext fun w => by simp [hFapp w, h])
  let G : (E → ℂ) →ₗ[ℂ] ℂ := ∑ j, φ (lam j) • LinearMap.proj (ν j)
  have hGapp : ∀ h : E → ℂ, G h = ∑ j, φ (lam j) * h (ν j) := by
    intro h
    simp [G]
  have hle : Submodule.span ℂ (f '' S) ≤ LinearMap.ker G := by
    rw [Submodule.span_le]
    rintro _ ⟨i, hi, rfl⟩
    have hgi : g i ∈ LinearMap.ker F := hFle (Submodule.subset_span ⟨i, hi, rfl⟩)
    rw [LinearMap.mem_ker, hFapp] at hgi
    change G (f i) = 0
    rw [hGapp]
    have : ∑ j, φ (lam j) * f i (ν j) = φ (∑ j, g i j * lam j) := by
      rw [map_sum]
      refine Finset.sum_congr rfl fun j _ => ?_
      rw [map_mul, hgf, mul_comm]
    rw [this, hgi, map_zero]
  have hzero : G (fun e => if e = ν j0 then 1 else 0) = 0 := by
    have hmem : (fun e => if e = ν j0 then (1 : ℂ) else 0) ∈ LinearMap.ker G :=
      hle (hf ▸ Submodule.mem_top)
    exact hmem
  rw [hGapp, Finset.sum_eq_single j0] at hzero
  · simp only [ite_true, mul_one] at hzero
    exact hj0 ((map_eq_zero_iff φ φ.injective).mp hzero)
  · intro j _ hj
    simp [hν.ne hj]
  · intro h
    exact absurd (Finset.mem_univ j0) h

open OAI.SiegelZeros.WeightedTorusJets in
/-- OAI's statement of Corollary 4 (copied verbatim), proved from `rectangle`. -/
theorem bridge_main
    {K κ : Type*} [Field K] [NumberField K] [Fintype κ]
    (a b : K) (v : Module.Basis (Fin 4) ℚ K)
    (hv : ∀ i, v i = ![1, a, b, a * b] i) (σ τ : K ≃ₐ[ℚ] K)
    (hσa : σ a = -a) (hσb : σ b = b) (hτa : τ a = a) (hτb : τ b = -b)
    (H N : ℕ) (hH : 0 < H) (hHN : H ≤ N)
    (n : κ → Fin 4 → ℕ) (hninj : Function.Injective n) (hn : ∀ j i, n j i < N) :
    let θ := fun j => ∑ i : Fin 4, (n j i : K) * ![1, a, b, a * b] i
    Submodule.span K
      ((fun α : Fin 3 → ℕ => fun j => θ j ^ α 0 * σ (θ j) ^ α 1 *
        (σ * τ) (θ j) ^ α 2) '' {α : Fin 3 → ℕ |
          (α 0 : ℝ) ≤ 32 * (H : ℝ) ^ (2 / 3 : ℝ) * (N : ℝ) ^ (4 / 3 : ℝ) ∧
          (α 1 : ℝ) ≤ 32 * (H : ℝ) ^ (-(1 / 3 : ℝ)) * (N : ℝ) ^ (4 / 3 : ℝ) ∧
          (α 2 : ℝ) ≤ 32 * (H : ℝ) ^ (-(1 / 3 : ℝ)) * (N : ℝ) ^ (4 / 3 : ℝ)}) = ⊤ := by
  intro θ
  classical
  let φ : K →+* ℂ := (IsAlgClosed.lift : K →ₐ[ℚ] ℂ).toRingHom
  obtain ⟨hc, D, hD⟩ := source_same_witness_hyperplane a b φ v hv σ τ hσa hσb hτa hτb
  set c := biquadraticCoefficients (φ a) (φ b) with hcdef
  let M : Matrix (Fin 3) (Fin 4) ℂ := fun j i => (D j : Fin 4 → ℂ) i
  let A : (Fin 4 → ℂ) →ₗ[ℂ] (Fin 3 → ℂ) := M.mulVecLin
  -- rows of `M` are linearly independent
  have hrows : LinearIndependent ℂ M.row :=
    D.linearIndependent.map' (Submodule.subtype _) (Submodule.ker_subtype _)
  have hrank : Module.finrank ℂ (LinearMap.range A) = 3 := by
    have := hrows.rank_matrix
    simpa [Matrix.rank, A] using this
  have hsurj : Function.Surjective A := by
    apply LinearMap.range_eq_top.mp
    apply Submodule.eq_top_of_finrank_eq
    rw [hrank]
    simp
  -- kernel
  have hform : ∀ x : Fin 4 → ℂ, biquadraticForm (φ a) (φ b) x = ∑ i, c i * x i := by
    intro x
    simp [biquadraticForm, dotProductBilin, dotProduct, c]
  have hcker : c ∈ LinearMap.ker A := by
    rw [LinearMap.mem_ker]
    funext j
    have h0 : biquadraticForm (φ a) (φ b) (D j : Fin 4 → ℂ) = 0 := (D j).2
    rw [hform] at h0
    change Matrix.mulVec M c j = 0
    simp only [Matrix.mulVec, dotProduct, M]
    rw [← h0]
    exact Finset.sum_congr rfl fun i _ => mul_comm (_ : ℂ) _
  have hc0 : c ≠ 0 := fun h => hc.ne_zero 0 (by rw [h]; rfl)
  have hkerdim : Module.finrank ℂ (LinearMap.ker A) = 1 := by
    have h := A.finrank_range_add_finrank_ker
    rw [hrank] at h
    simp only [Module.finrank_fintype_fun_eq_card, Fintype.card_fin] at h
    omega
  have hker : LinearMap.ker A = Submodule.span ℂ {c} := by
    symm
    apply Submodule.eq_of_le_of_finrank_eq
    · rw [Submodule.span_le, Set.singleton_subset_iff]
      exact hcker
    · rw [finrank_span_singleton hc0, hkerdim]
  have hspan := rectangle A hsurj c hker hc H N hH hHN
  -- the column embedding
  let ν : κ → (Fin 4 → Fin N) := fun j i => ⟨n j i, hn j i⟩
  have hν : Function.Injective ν := by
    intro j j' h
    apply hninj
    funext i
    exact congrArg Fin.val (congrFun h i)
  have hAk : ∀ (x : Fin 4 → ℂ) (k : Fin 3), A x k =
      ∑ i, φ ((![![1, a, b, a * b], (fun i => σ (![1, a, b, a * b] i)),
          (fun i => (σ * τ) (![1, a, b, a * b] i))] : Fin 3 → Fin 4 → K) k i) * x i := by
    intro x k
    change Matrix.mulVec M x k = _
    simp only [Matrix.mulVec, dotProduct, M, hD]
  refine bridge_descent φ ν hν ?_ hspan
  intro α j
  have e0 : φ (θ j) = A (fun i => ((ν j i : ℕ) : ℂ)) 0 := by
    rw [hAk]
    simp only [θ, map_sum, map_mul, map_natCast, ν]
    refine Finset.sum_congr rfl fun i _ => ?_
    simp [mul_comm]
  have e1 : φ (σ (θ j)) = A (fun i => ((ν j i : ℕ) : ℂ)) 1 := by
    rw [hAk]
    simp only [θ, map_sum, map_mul, map_natCast, ν]
    refine Finset.sum_congr rfl fun i _ => ?_
    simp [mul_comm]
  have e2 : φ ((σ * τ) (θ j)) = A (fun i => ((ν j i : ℕ) : ℂ)) 2 := by
    rw [hAk]
    simp only [θ, map_sum, map_mul, map_natCast, ν]
    refine Finset.sum_congr rfl fun i _ => ?_
    simp [mul_comm]
  rw [map_mul, map_mul, map_pow, map_pow, map_pow, e0, e1, e2]

/-- OAI's Corollary 4, proved via the paper's Lemma 3 instead of the multiplicity estimate. -/
theorem actual_biquadratic_rectangle_span_via_lemma3 :
    type_of% @OAI.SiegelZeros.WeightedTorusJets.actual_biquadratic_rectangle_span := by
  intro K κ _ _ _ a b v hv σ τ hσa hσb hτa hτb H N hH hHN n hninj hn
  exact bridge_main a b v hv σ τ hσa hσb hτa hτb H N hH hHN n hninj hn

end

end Lemma3
