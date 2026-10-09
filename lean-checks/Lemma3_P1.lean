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

lemma p1_dot_self_nonneg (v : Fin 4 → ℝ) : 0 ≤ dotProduct v v :=
  Finset.sum_nonneg fun i _ => mul_self_nonneg (v i)

lemma p1_coord_le_sqd (a z : Fin 4 → ℝ) (i : Fin 4) :
    (a i - z i) * (a i - z i) ≤ sqd a z := by
  unfold sqd dotProduct
  exact Finset.single_le_sum (f := fun j => (a - z) j * (a - z) j)
    (fun j _ => mul_self_nonneg _) (Finset.mem_univ i)

/-- The variational inequality for a nearest point in a convex set. -/
lemma p1_var_ineq (K : Set (Fin 4 → ℝ)) (hKcv : Convex ℝ K) (a y : Fin 4 → ℝ) (hy : y ∈ K)
    (hmin : ∀ z ∈ K, sqd a y ≤ sqd a z) : ∀ x ∈ K, dotProduct (a - y) (x - y) ≤ 0 := by
  intro x hx
  by_contra hpos
  push Not at hpos
  set c := dotProduct (a - y) (x - y) with hc
  set b := dotProduct (x - y) (x - y) with hb
  have hb0 : 0 ≤ b := p1_dot_self_nonneg _
  set t := c / (c + b) with ht
  have hcb : 0 < c + b := by linarith
  have ht0 : 0 < t := div_pos hpos hcb
  have ht1 : t ≤ 1 := by rw [ht, div_le_one hcb]; linarith
  have htb : t * b ≤ c := by
    rw [ht, div_mul_eq_mul_div, div_le_iff₀ hcb]; nlinarith
  have hz : (1 - t) • y + t • x ∈ K := hKcv hy hx (by linarith) ht0.le (by ring)
  have key := hmin _ hz
  have expand : sqd a ((1 - t) • y + t • x) = sqd a y - 2 * t * c + t ^ 2 * b := by
    simp only [sqd, hc, hb, dotProduct, Pi.sub_apply, Pi.add_apply, Pi.smul_apply,
      smul_eq_mul]
    rw [Finset.mul_sum, Finset.mul_sum, ← Finset.sum_sub_distrib, ← Finset.sum_add_distrib]
    refine Finset.sum_congr rfl fun i _ => ?_
    ring
  rw [expand] at key
  have h2 : 2 * t * c ≤ t ^ 2 * b := by linarith
  have h3 : 2 * c ≤ t * b := by
    have : t * (2 * c) ≤ t * (t * b) := by nlinarith
    exact le_of_mul_le_mul_left this ht0
  linarith

/-- Step 5 and the nearest-point inequality. Among the lattice points in `W`, one, `m`,
is at least distance from the compact convex set `K`; `y` is its nearest point in `K`.
(The distance from `m'` to `K` is the infimum of `sqd (zR m') z` over `z ∈ K`.) -/
theorem exists_nearest (K : Set (Fin 4 → ℝ)) (hKc : IsCompact K) (hKcv : Convex ℝ K)
    (hKne : K.Nonempty) (W : Set (Fin 4 → ℤ)) (hW : W.Nonempty) :
    ∃ m ∈ W, ∃ y ∈ K, (∀ x ∈ K, dotProduct (zR m - y) (x - y) ≤ 0) ∧
      ∀ m' ∈ W, ∀ z ∈ K, sqd (zR m) y ≤ sqd (zR m') z := by
  classical
  have hcont : ∀ a, ContinuousOn (fun z => sqd a z) K := fun a => by
    unfold sqd dotProduct
    fun_prop
  have hsel : ∀ a : Fin 4 → ℝ, ∃ y ∈ K, ∀ z ∈ K, sqd a y ≤ sqd a z := fun a => by
    obtain ⟨y, hy, hmin⟩ := hKc.exists_isMinOn hKne (hcont a)
    exact ⟨y, hy, fun z hz => hmin hz⟩
  choose g hgK hgmin using hsel
  obtain ⟨m0, hm0⟩ := hW
  set D := sqd (zR m0) (g (zR m0)) with hD
  obtain ⟨r, hr⟩ := (Metric.isBounded_iff_subset_closedBall (0 : Fin 4 → ℝ)).1 hKc.isBounded
  have hRb : ∀ z ∈ K, ∀ i, |z i| ≤ r := by
    intro z hz i
    have h1 := hr hz
    rw [mem_closedBall_zero_iff] at h1
    have h2 := norm_le_pi_norm z i
    rw [Real.norm_eq_abs] at h2
    linarith
  set W' : Set (Fin 4 → ℤ) := {m' | m' ∈ W ∧ sqd (zR m') (g (zR m')) ≤ D} with hW'
  set C : ℝ := r + 1 + D with hC
  set B : ℤ := ⌈C⌉ with hB
  have hfin : W'.Finite := by
    refine (Set.finite_Icc (fun _ : Fin 4 => -B) (fun _ => B)).subset ?_
    rintro m' ⟨-, hm'D⟩
    have hbd : ∀ i, |(m' i : ℝ)| ≤ C := by
      intro i
      set z := g (zR m')
      have hz := hRb z (hgK _) i
      have hc := p1_coord_le_sqd (zR m') z i
      simp only [zR] at hc
      set e := (m' i : ℝ) - z i
      have he : |e| ≤ e * e + 1 := by
        rcases abs_cases e with ⟨h, _⟩ | ⟨h, _⟩ <;> rw [h] <;> nlinarith
      have : (m' i : ℝ) = z i + e := by simp [e]
      rw [this]
      calc |z i + e| ≤ |z i| + |e| := abs_add_le _ _
        _ ≤ C := by rw [hC]; linarith
    have hCB : C ≤ (B : ℝ) := Int.le_ceil C
    constructor
    · intro i
      have h := (abs_le.1 (hbd i)).1
      have : ((-B : ℤ) : ℝ) ≤ (m' i : ℝ) := by push_cast; linarith
      exact_mod_cast this
    · intro i
      have h := (abs_le.1 (hbd i)).2
      have : (m' i : ℝ) ≤ ((B : ℤ) : ℝ) := by linarith
      exact_mod_cast this
  obtain ⟨m, hmW', hmmin⟩ :=
    Set.exists_min_image W' (fun m' => sqd (zR m') (g (zR m'))) hfin ⟨m0, hm0, le_rfl⟩
  refine ⟨m, hmW'.1, g (zR m), hgK _, p1_var_ineq K hKcv _ _ (hgK _) (hgmin _), ?_⟩
  intro m' hm' z hz
  by_cases h' : sqd (zR m') (g (zR m')) ≤ D
  · exact (hmmin m' ⟨hm', h'⟩).trans (hgmin _ z hz)
  · push Not at h'
    exact (hmW'.2.trans h'.le).trans (hgmin _ z hz)

/-- Step 6. `y/4` lies in the face `G` of `P = conv S` maximizing `h·`. Here the face is
given by its points of `S`, so this also records the unstated fact that `G = conv(S ∩ G)`. -/
theorem quarter_mem_face {ι : Type*} (p : ι → Fin 4 → ℝ) (S : Finset ι) (h y : Fin 4 → ℝ)
    (hy : y ∈ (4 : ℝ) • convexHull ℝ (p '' S))
    (hmax : ∀ x ∈ (4 : ℝ) • convexHull ℝ (p '' S), dotProduct h (x - y) ≤ 0) :
    (1 / 4 : ℝ) • y ∈ convexHull ℝ
      (p '' {s | s ∈ S ∧ ∀ s' ∈ S, dotProduct h (p s') ≤ dotProduct h (p s)}) := by
  classical
  set T : Finset (Fin 4 → ℝ) := S.image p with hT
  have hTc : p '' (S : Set ι) = (T : Set (Fin 4 → ℝ)) := by simp [hT]
  obtain ⟨x, hx, rfl⟩ := Set.mem_smul_set.1 hy
  have hq : (1 / 4 : ℝ) • (4 : ℝ) • x = x := by rw [smul_smul]; norm_num
  rw [hq]
  rw [hTc] at hx hmax
  obtain ⟨w, hw0, hw1, hwx⟩ := Finset.mem_convexHull'.1 hx
  set a := dotProduct h x with ha
  -- every point of `T` has `h·v ≤ a`
  have hle : ∀ v ∈ T, dotProduct h v ≤ a := by
    intro v hv
    have h1 := hmax ((4 : ℝ) • v)
      (Set.smul_mem_smul_set (subset_convexHull ℝ _ (Finset.mem_coe.2 hv)))
    rw [dotProduct_sub, dotProduct_smul, smul_eq_mul, dotProduct_smul,
      smul_eq_mul] at h1
    linarith
  have hsum : ∑ v ∈ T, w v * (a - dotProduct h v) = 0 := by
    have e1 : a = ∑ v ∈ T, w v * dotProduct h v := by
      rw [ha, ← hwx, dotProduct_sum]
      simp [dotProduct_smul]
    simp only [mul_sub, Finset.sum_sub_distrib, ← Finset.sum_mul, hw1, one_mul]
    linarith
  have hzero := (Finset.sum_eq_zero_iff_of_nonneg
    (fun v hv => mul_nonneg (hw0 v hv) (sub_nonneg.2 (hle v hv)))).1 hsum
  set G : Finset (Fin 4 → ℝ) := T.filter (fun v => ∀ v' ∈ T, dotProduct h v' ≤ dotProduct h v)
    with hG
  have hout : ∀ v ∈ T, v ∉ G → w v = 0 := by
    intro v hv hvG
    have hnot : ¬ ∀ v' ∈ T, dotProduct h v' ≤ dotProduct h v := by
      intro hc; exact hvG (Finset.mem_filter.2 ⟨hv, hc⟩)
    push Not at hnot
    obtain ⟨v', hv', hlt⟩ := hnot
    have hlt' : dotProduct h v < a := lt_of_lt_of_le hlt (hle v' hv')
    have := hzero v hv
    rcases mul_eq_zero.1 this with h0 | h0
    · exact h0
    · exact absurd h0 (by linarith)
  have hGT : G ⊆ T := Finset.filter_subset _ _
  have hsub : ↑G ⊆ p '' {s | s ∈ S ∧ ∀ s' ∈ S, dotProduct h (p s') ≤ dotProduct h (p s)} := by
    intro v hv
    rw [Finset.mem_coe, Finset.mem_filter] at hv
    obtain ⟨hvT, hvmax⟩ := hv
    obtain ⟨s, hs, rfl⟩ := Finset.mem_image.1 hvT
    exact ⟨s, ⟨hs, fun s' hs' => hvmax (p s') (Finset.mem_image_of_mem p hs')⟩, rfl⟩
  apply convexHull_mono hsub
  rw [Finset.mem_convexHull']
  refine ⟨w, fun v hv => hw0 v (hGT hv), ?_, ?_⟩
  · rw [← hw1]
    exact Finset.sum_subset hGT (fun v hv hvG => hout v hv hvG)
  · rw [← hwx]
    exact Finset.sum_subset hGT (fun v hv hvG => by rw [hout v hv hvG, zero_smul])

end

end Lemma3

#print axioms Lemma3.exists_nearest
#print axioms Lemma3.quarter_mem_face
