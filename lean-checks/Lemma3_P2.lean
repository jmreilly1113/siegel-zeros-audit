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

end

end Lemma3

#print axioms Lemma3.exists_heavy_vertex
#print axioms Lemma3.closer_point
