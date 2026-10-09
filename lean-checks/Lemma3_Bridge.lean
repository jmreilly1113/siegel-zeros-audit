import Mathlib
import OAI.NumberTheory.SiegelZeros.Main
open MvPolynomial Pointwise
namespace Lemma3
noncomputable section
/-- Corollary 4, proved elsewhere (stub replaced on merge). -/
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
  sorry

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
#print axioms Lemma3.actual_biquadratic_rectangle_span_via_lemma3
