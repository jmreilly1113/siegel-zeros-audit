import Mathlib
import OAI.NumberTheory.SiegelZeros.Main

/-!
# Lemma 3 (`lem:interpolation`) of "Uniform exclusion of Landau–Siegel zeros": skeleton

Paper: refs/siegel-paper.tex lines 252–267 (statement) and 269–407 (proof).
Plan: docs/plan-remaining-gaps.md, step 3c.

`interpolation` is the paper's statement. Its proof below is complete *given* the
sub-lemmas, which are stated separately and are proved in the piece files and merged here. Each sub-lemma is
one self-contained piece of the paper's proof and can be proved independently.
The step numbers refer to docs/lemma3-audit.md.

| Piece | Sub-lemmas | Paper steps |
|---|---|---|
| 1. Nearest point and face | `exists_nearest`, `quarter_mem_face` | 5–7 |
| 2. Carathéodory and the move off the face | `exists_heavy_vertex`, `closer_point` | 8–11 |
| 3. Rational hyperplane | `exists_int_hyperplane`, `int_comb_ne_zero` | 12 |
| 4. Lagrange polynomial | `exists_lagrange` | 13–14 |
| 5. Counting and degrees | `exists_annihilator`, `four_hull_subset_cube`, `exists_vanishing`, `exists_lattice_nonvanishing`, `exists_translate` | 1–4, 15 |
-/

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

/-! ## Sub-lemmas, proved (merged from the five piece files) -/

/-! ### Piece 1 (from lean-checks/Lemma3_P1.lean) -/
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

/-! ### Piece 2 (from lean-checks/Lemma3_P2.lean) -/
/-! ## Piece 2: Carathéodory and the move off the face -/

theorem p2_dot_expand (h w : Fin 4 → ℝ) (s : ℝ) :
    dotProduct (h + s • w) (h + s • w) =
      dotProduct h h + 2 * s * dotProduct h w + s ^ 2 * dotProduct w w := by
  simp only [add_dotProduct, dotProduct_add, smul_dotProduct, dotProduct_smul, smul_eq_mul,
    dotProduct_comm w h]
  ring

theorem p2_dot_self_nonneg (w : Fin 4 → ℝ) : 0 ≤ dotProduct w w := by
  unfold dotProduct
  exact Finset.sum_nonneg (fun i _ => mul_self_nonneg (w i))

/-- Steps 7–8 (eq:vertex). A point of the hull of points lying in a hyperplane `h· = const`
(`h ≠ 0`, so affine dimension ≤ 3) is a combination of at most four of them, one with
coefficient ≥ 1/4; call it `u`. Then `4x − u ∈ 3·conv`. -/
theorem exists_heavy_vertex {ι : Type*} (p : ι → Fin 4 → ℝ) (T : Set ι) (h : Fin 4 → ℝ)
    (hh : h ≠ 0) (hT : ∀ s ∈ T, ∀ s' ∈ T, dotProduct h (p s) = dotProduct h (p s'))
    (x : Fin 4 → ℝ) (hx : x ∈ convexHull ℝ (p '' T)) :
    ∃ u ∈ T, (4 : ℝ) • x - p u ∈ (3 : ℝ) • convexHull ℝ (p '' T) := by
  classical
  obtain ⟨ι', hfin, z, w, hzs, hai, hw0, hw1, hwx⟩ := eq_pos_convex_span_of_mem_convexHull hx
  let f : (Fin 4 → ℝ) →ₗ[ℝ] ℝ :=
    { toFun := fun v => dotProduct h v
      map_add' := fun a b => dotProduct_add h a b
      map_smul' := fun c v => by simp [dotProduct_smul] }
  have hker : LinearMap.ker f ≠ ⊤ := by
    intro htop
    have hm : h ∈ LinearMap.ker f := htop ▸ Submodule.mem_top
    exact hh (dotProduct_self_eq_zero.1 hm)
  have hlt := Submodule.finrank_lt hker
  rw [Module.finrank_fin_fun] at hlt
  have hvs : vectorSpan ℝ (Set.range z) ≤ LinearMap.ker f := by
    rw [vectorSpan_def, Submodule.span_le]
    rintro _ ⟨a, ha, b, hb, rfl⟩
    obtain ⟨i, rfl⟩ := ha
    obtain ⟨j, rfl⟩ := hb
    obtain ⟨si, hsi, hzi⟩ := hzs ⟨i, rfl⟩
    obtain ⟨sj, hsj, hzj⟩ := hzs ⟨j, rfl⟩
    show dotProduct h (z i - z j) = 0
    rw [dotProduct_sub, ← hzi, ← hzj, hT si hsi sj hsj, sub_self]
  have hne : Nonempty ι' := by
    by_contra hem
    rw [not_nonempty_iff] at hem
    simp at hw1
  have hcard : Fintype.card ι' ≤ 4 := by
    obtain ⟨k, hk⟩ : ∃ k, Fintype.card ι' = k + 1 :=
      Nat.exists_eq_succ_of_ne_zero Fintype.card_ne_zero
    have h1 := hai.finrank_vectorSpan hk
    have h2 := Submodule.finrank_mono hvs
    omega
  obtain ⟨i, hi⟩ : ∃ i, 1 / 4 ≤ w i := by
    by_contra hc
    push Not at hc
    have hs : ∑ j, w j < ∑ _j : ι', (1 / 4 : ℝ) :=
      Finset.sum_lt_sum_of_nonempty Finset.univ_nonempty (fun j _ => hc j)
    rw [Finset.sum_const, Finset.card_univ, nsmul_eq_mul] at hs
    have : (Fintype.card ι' : ℝ) ≤ 4 := by exact_mod_cast hcard
    linarith
  obtain ⟨u, huT, hzu⟩ := hzs ⟨i, rfl⟩
  refine ⟨u, huT, ?_⟩
  set v : ι' → ℝ := fun j => (4 * w j - if j = i then 1 else 0) / 3 with hvdef
  have hv0 : ∀ j ∈ Finset.univ, 0 ≤ v j := by
    intro j _
    have := hw0 j
    simp only [hvdef]
    split_ifs with hj
    · subst hj; linarith
    · linarith
  have hv1 : ∑ j, v j = 1 := by
    simp only [hvdef, ← Finset.sum_div, Finset.sum_sub_distrib, ← Finset.mul_sum, hw1]
    simp
    norm_num
  have hmem : ∑ j, v j • z j ∈ convexHull ℝ (p '' T) :=
    (convex_convexHull ℝ _).sum_mem hv0 hv1 (fun j _ => subset_convexHull ℝ _ (hzs ⟨j, rfl⟩))
  have hterm : ∀ j, (3 : ℝ) • (v j • z j) =
      (4 : ℝ) • (w j • z j) - (if j = i then z j else 0) := by
    intro j
    by_cases hj : j = i
    · simp only [hvdef, hj, ↓reduceIte]
      module
    · simp only [hvdef, hj, ↓reduceIte]
      module
  have heq : (3 : ℝ) • ∑ j, v j • z j = (4 : ℝ) • x - p u := by
    rw [Finset.smul_sum, Finset.sum_congr rfl (fun j _ => hterm j), Finset.sum_sub_distrib,
      ← Finset.smul_sum, hwx, hzu]
    simp
  rw [← heq]
  exact Set.smul_mem_smul_set hmem

/-- Steps 9–10 (eq:distance). With `m = y + h`, `y' = y + n − u ∈ 4P` and
`h·(u − n) > 0`, some point of `4P` is closer to `m' = m + n − u` than `y` is to `m`. -/
theorem closer_point (P : Set (Fin 4 → ℝ)) (hP : Convex ℝ P) (h y u n : Fin 4 → ℝ)
    (hyu : y - u ∈ (3 : ℝ) • P) (hn : n ∈ P) (hy : y ∈ (4 : ℝ) • P)
    (hpos : 0 < dotProduct h (u - n)) :
    ∃ z ∈ (4 : ℝ) • P, sqd (y + h + (n - u)) z < sqd (y + h) y := by
  set w := n - u with hwdef
  set a := -dotProduct h w with hadef
  set b := dotProduct w w with hbdef
  have ha : 0 < a := by
    have e : dotProduct h (u - n) = -dotProduct h w := by
      rw [hwdef, ← dotProduct_neg, neg_sub]
    rw [hadef, ← e]
    exact hpos
  have hb : 0 ≤ b := p2_dot_self_nonneg w
  set s := a / (a + b) with hsdef
  have hab : 0 < a + b := by linarith
  have hs : s * (a + b) = a := div_mul_cancel₀ a (ne_of_gt hab)
  have hs0 : 0 < s := div_pos ha hab
  have hs1 : s ≤ 1 := (div_le_one hab).2 (by linarith)
  have h4 : (4 : ℝ) • P = (3 : ℝ) • P + (1 : ℝ) • P := by
    rw [← hP.add_smul (by norm_num) (by norm_num)]
    norm_num
  have hyw : y + w ∈ (4 : ℝ) • P := by
    rw [h4]
    have e : y + w = (y - u) + n := by rw [hwdef]; abel
    rw [e]
    exact Set.add_mem_add hyu (by rw [one_smul]; exact hn)
  have hconv : Convex ℝ ((4 : ℝ) • P) := hP.smul 4
  refine ⟨y + (1 - s) • w, ?_, ?_⟩
  · have := hconv.add_smul_sub_mem hy hyw ⟨by linarith, by linarith⟩ (t := 1 - s)
    simpa using this
  · have e1 : y + h + w - (y + (1 - s) • w) = h + s • w := by module
    have e2 : y + h - y = h := by abel
    unfold sqd
    rw [e1, e2, p2_dot_expand]
    have e3 : s ^ 2 * b = s * a - s ^ 2 * a := by linear_combination s * hs
    have e4 : dotProduct h w = -a := by rw [hadef]; ring
    rw [← hbdef, e3, e4]
    nlinarith [mul_pos hs0 ha, mul_pos (mul_pos hs0 hs0) ha]

/-! ### Piece 3 (from lean-checks/Lemma3_P3.lean) -/
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

/-! ### Piece 4 (from lean-checks/Lemma3_P4.lean) -/
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

/-! ### Piece 5 (from lean-checks/Lemma3_P5.lean) -/
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

/-! ## The lemma -/

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
        eval (A (fun i => ((n i : ℕ) : ℂ))) (B : MvPolynomial (Fin 3) ℂ)) := by
  classical
  by_contra hns
  -- Step 1: the annihilating weights `v`.
  have hN1 : (1 : ℤ) ≤ N := by exact_mod_cast hN
  obtain ⟨v, hv0, hmom⟩ :=
    exists_annihilator t (fun j => by linarith [ht j]) _ hns
  have hfC : ∀ n : Fin 4 → Fin N, (fun i => ((n i : ℕ) : ℂ)) = zC (emb n) := by
    intro n; ext i; simp [zC, emb]
  -- Step 2: `S`, `P`, `𝒦`.
  set S : Finset (Fin 4 → Fin N) := Finset.univ.filter (fun n => v n ≠ 0) with hSdef
  set p : (Fin 4 → Fin N) → Fin 4 → ℝ := fun n => zR (emb n) with hpdef
  set P : Set (Fin 4 → ℝ) := convexHull ℝ (p '' S) with hPdef
  set K : Set (Fin 4 → ℝ) := (4 : ℝ) • P with hKdef
  have hSne : S.Nonempty := by
    by_contra hS
    apply hv0
    ext n
    by_contra hn
    exact hS ⟨n, by simpa [hSdef] using hn⟩
  -- Step 3: `R`.
  set b : Fin 3 → ℕ := fun j => (t j - 3 * ((N : ℤ) - 1)).toNat with hbdef
  have hb : ∀ j, ((b j : ℕ) : ℤ) = t j - 3 * ((N : ℤ) - 1) := fun j =>
    Int.toNat_of_nonneg (by linarith [ht j])
  set Z : Finset (Fin 4 → ℤ) :=
    (Fintype.piFinset fun _ => Finset.Icc (0 : ℤ) (4 * ((N : ℤ) - 1))).filter
      (fun m => zR m ∈ K) with hZdef
  have hZcard : Z.card < ∏ j, (b j + 1) := by
    have h1 : Z.card ≤ ((4 * (N : ℤ) - 3).toNat) ^ 4 := by
      refine (Finset.card_filter_le _ _).trans (le_of_eq ?_)
      rw [Fintype.card_piFinset]
      simp only [Int.card_Icc, Finset.prod_const, Finset.card_univ, Fintype.card_fin]
      congr 2
      ring
    have h2 : (((4 * (N : ℤ) - 3).toNat ^ 4 : ℕ) : ℤ) < ((∏ j, (b j + 1) : ℕ) : ℤ) := by
      push_cast
      rw [Int.toNat_of_nonneg (by omega)]
      simp only [hb]
      exact hbudget
    exact lt_of_le_of_lt h1 (by exact_mod_cast h2)
  obtain ⟨R, hR0, hRdeg, hRZ⟩ := exists_vanishing A b Z hZcard
  have hpbox : ∀ x ∈ p '' S, ∀ i, 0 ≤ x i ∧ x i ≤ (N : ℝ) - 1 := by
    rintro _ ⟨s, -, rfl⟩ i
    have hlt := (s i).isLt
    refine ⟨by simp [hpdef, zR, emb], ?_⟩
    have : ((s i : ℕ) : ℝ) + 1 ≤ N := by exact_mod_cast hlt
    simp only [hpdef, zR, emb, Int.cast_natCast]
    linarith
  have hRK : ∀ m : Fin 4 → ℤ, zR m ∈ K → eval (A (zC m)) R = 0 := by
    intro m hm
    apply hRZ
    have hc4 := four_hull_subset_cube _ _ hpbox _ hm
    simp only [hZdef, Finset.mem_filter, Fintype.mem_piFinset, Finset.mem_Icc]
    refine ⟨fun i => ?_, hm⟩
    obtain ⟨h0, h1⟩ := hc4 i
    simp only [zR] at h0 h1
    constructor
    · exact_mod_cast h0
    · have : ((m i : ℤ) : ℝ) ≤ ((4 * ((N : ℤ) - 1) : ℤ) : ℝ) := by push_cast; linarith
      exact_mod_cast this
  -- Step 4: lattice points where `R ∘ A` does not vanish.
  set W : Set (Fin 4 → ℤ) := {m | eval (A (zC m)) R ≠ 0} with hWdef
  have hW : W.Nonempty := exists_lattice_nonvanishing A hA R hR0
  -- Step 5: the nearest such point `m`, and `y`, `h`.
  have hKc : IsCompact K := by
    have : IsCompact P :=
      Set.Finite.isCompact_convexHull (𝕜 := ℝ) ((Finset.finite_toSet S).image p)
    simpa [hKdef] using this.image (continuous_const_smul (4 : ℝ))
  have hKcv : Convex ℝ K := (convex_convexHull ℝ _).smul 4
  have hKne : K.Nonempty := by
    obtain ⟨s, hs⟩ := hSne
    exact ⟨(4 : ℝ) • p s, Set.smul_mem_smul_set (subset_convexHull ℝ _ ⟨s, hs, rfl⟩)⟩
  obtain ⟨m, hmW, y, hyK, hnear, hmin⟩ := exists_nearest K hKc hKcv hKne W hW
  set h : Fin 4 → ℝ := zR m - y with hhdef
  have hh : h ≠ 0 := by
    intro h0
    have : zR m = y := sub_eq_zero.1 h0
    exact hmW (hRK m (this ▸ hyK))
  -- Step 6: the face `G`, given by its points `F` of `S`.
  set F : Set (Fin 4 → Fin N) :=
    {s | s ∈ S ∧ ∀ s' ∈ S, dotProduct h (p s') ≤ dotProduct h (p s)} with hFdef
  have hq := quarter_mem_face p S h y hyK hnear
  have hFpair : ∀ s ∈ F, ∀ s' ∈ F, dotProduct h (p s) = dotProduct h (p s') :=
    fun s hs s' hs' => le_antisymm (hs'.2 s hs.1) (hs.2 s' hs'.1)
  -- Steps 7–8: the vertex `u`.
  obtain ⟨u, huF, hu4⟩ := exists_heavy_vertex p F h hh hFpair _ hq
  have hyu : y - p u ∈ (3 : ℝ) • P := by
    have e : (4 : ℝ) • ((1 / 4 : ℝ) • y) = y := by
      rw [smul_smul]; norm_num
    rw [e] at hu4
    exact Set.smul_set_mono (convexHull_mono (Set.image_mono fun s hs => hs.1)) hu4
  -- Steps 9–11: `R` vanishes at `m + n − u` for `n ∈ S` off the face.
  have hoff : ∀ n ∈ S, n ∉ F → eval (A (zC (m + emb n - emb u))) R = 0 := by
    intro n hn hnF
    have hpos : 0 < dotProduct h (p u - p n) := by
      have : ∃ s' ∈ S, dotProduct h (p n) < dotProduct h (p s') := by
        by_contra hc'
        push Not at hc'
        exact hnF ⟨hn, hc'⟩
      obtain ⟨s', hs', hlt⟩ := this
      have := huF.2 s' hs'
      rw [dotProduct_sub]
      linarith
    have hnP : p n ∈ P := subset_convexHull ℝ _ ⟨n, hn, rfl⟩
    obtain ⟨z, hzK, hz⟩ :=
      closer_point P (convex_convexHull ℝ _) h y (p u) (p n) hyu hnP hyK hpos
    by_contra hne
    have hle := hmin (m + emb n - emb u) hne z hzK
    have e1 : zR m = y + h := by simp [hhdef]
    have e2 : zR (m + emb n - emb u) = y + h + (p n - p u) := by
      ext i; simp [zR, hpdef, hhdef]; ring
    rw [e1] at hle
    rw [e2] at hle
    linarith
  -- Step 12: the integer hyperplane `ℋ` through the face, and `r·c ≠ 0`.
  obtain ⟨r, hr0, k, hrk⟩ := exists_int_hyperplane (emb '' F) h hh (by
    rintro _ ⟨s, hs, rfl⟩ _ ⟨s', hs', rfl⟩
    exact hFpair s hs s' hs')
  have hrc := int_comb_ne_zero c hc r hr0
  -- Steps 13–14: the Lagrange polynomial `Q`.
  obtain ⟨Q, hQdeg, hQu, hQ0⟩ :=
    exists_lagrange A hA c hker r hrc k N F (fun n hn => hrk _ ⟨n, hn, rfl⟩) u huF
  -- Step 15: `B = Q · R(z + A(m − u)) ∈ 𝒫_t`.
  obtain ⟨R', hR'deg, hR'eval⟩ := exists_translate R (A (zC (m - emb u)))
  have hB : Q * R' ∈ Pt t := by
    intro j
    have h1 := degreeOf_mul_le j Q R'
    have h2 := degreeOf_le_totalDegree Q j
    have h3 := hR'deg j
    have h4 := hRdeg j
    have h5 := hb j
    have h6 : ((Q * R').degreeOf j : ℤ) ≤ (3 * (N - 1) : ℕ) + (b j : ℤ) := by
      exact_mod_cast (h1.trans (Nat.add_le_add (h2.trans hQdeg) (h3.trans h4)))
    have h7 : (((3 * (N - 1) : ℕ)) : ℤ) = 3 * ((N : ℤ) - 1) := by
      rw [Nat.cast_mul, Nat.cast_sub hN]; simp
    linarith
  -- Step 16: the moment sum equals `v_u R(Am) ≠ 0`.
  have hsum := hmom _ hB
  have hterm : ∀ n : Fin 4 → Fin N,
      v n * eval (A (fun i => ((n i : ℕ) : ℂ))) (Q * R') =
        v n * (eval (A (zC (emb n))) Q * eval (A (zC (m + emb n - emb u))) R) := by
    intro n
    have e : zC (emb n) + zC (m - emb u) = zC (m + emb n - emb u) := by
      ext i; simp only [zC, Pi.add_apply, Pi.sub_apply, Int.cast_add, Int.cast_sub]; ring
    rw [hfC n, eval_mul, hR'eval, ← map_add, e]
  simp only [hterm] at hsum
  rw [Finset.sum_eq_single u] at hsum
  · have hu : v u ≠ 0 := by
      have := huF.1
      simpa [hSdef] using this
    rw [hQu, one_mul, add_sub_cancel_right] at hsum
    exact mul_ne_zero hu hmW hsum
  · intro n _ hnu
    by_cases hvn : v n = 0
    · simp [hvn]
    have hnS : n ∈ S := by simp [hSdef, hvn]
    by_cases hnF : n ∈ F
    · rw [hQ0 n hnF hnu]; simp
    · rw [hoff n hnS hnF]; simp
  · intro hu; exact absurd (Finset.mem_univ u) hu


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

/-! ## Dependency check: does a proof use OAI's multiplicity-estimate route? -/
open Lean Elab Command in
/-- Lists every constant in the transitive closure (types and values) of `n` whose last name
component is one of the given strings. -/
elab "#find_deps " n:ident " [" xs:str,* "]" : command => do
  let env ← getEnv
  let targets := xs.getElems.toList.map (·.getString)
  let root ← liftCoreM <| realizeGlobalConstNoOverloadWithInfo n
  let mut seen : NameSet := {}
  let mut stack : List Name := [root]
  let mut hits : Array Name := #[]
  while !stack.isEmpty do
    let c := stack.head!
    stack := stack.tail!
    if seen.contains c then continue
    seen := seen.insert c
    if let .str _ s := c then
      if targets.contains s && c != root then hits := hits.push c
    match env.find? c with
    | some ci =>
      let v : Option Expr := match ci with
        | .thmInfo t => some t.value
        | .defnInfo d => some d.value
        | .opaqueInfo o => some o.value
        | _ => none
      let refs := ci.type.getUsedConstants ++ (v.map (·.getUsedConstants) |>.getD #[])
      for r in refs do
        if !seen.contains r then stack := r :: stack
    | none => pure ()
  logInfo m!"{root}: {seen.size} constants in closure; matches: {hits}"

#find_deps Lemma3.actual_biquadratic_rectangle_span_via_lemma3 ["uniform_rectangular_multiplicity", "source_rectangle_span_of_polynomial_zero_test", "actual_biquadratic_rectangle_span"]
-- control: OAI's own proof should match
#find_deps OAI.SiegelZeros.WeightedTorusJets.actual_biquadratic_rectangle_span ["uniform_rectangular_multiplicity", "source_rectangle_span_of_polynomial_zero_test", "actual_biquadratic_rectangle_span"]

#check @Lemma3.rectangle
#print axioms Lemma3.interpolation
#print axioms Lemma3.rectangle
#print axioms Lemma3.actual_biquadratic_rectangle_span_via_lemma3
