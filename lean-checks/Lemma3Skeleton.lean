import Mathlib

/-!
# Lemma 3 (`lem:interpolation`) of "Uniform exclusion of Landau–Siegel zeros": skeleton

Paper: refs/siegel-paper.tex lines 252–267 (statement) and 269–407 (proof).
Plan: docs/plan-remaining-gaps.md, step 3c.

`interpolation` is the paper's statement. Its proof below is complete *given* the
sub-lemmas, which are stated separately and still carry `sorry`. Each sub-lemma is
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

/-! ## Sub-lemmas (each still `sorry`) -/

/-- Step 1 (eq:moments). If evaluation on `𝒫_t` is not surjective, a nonzero
weighting `v` of the points annihilates every `B ∈ 𝒫_t`. (`t ≥ 0` makes `𝒫_t` a subspace;
without it the claim fails when `ι` is empty.) -/
theorem exists_annihilator {ι : Type*} [Fintype ι] (t : Fin 3 → ℤ) (ht0 : ∀ j, 0 ≤ t j)
    (f : ι → Fin 3 → ℂ) (h : ¬ Function.Surjective
      (fun B : Pt t => fun n => eval (f n) (B : MvPolynomial (Fin 3) ℂ))) :
    ∃ v : ι → ℂ, v ≠ 0 ∧ ∀ B ∈ Pt t, ∑ n, v n * eval (f n) B = 0 := by
  sorry

/-- Step 2. `𝒦 = 4P ⊂ [0, 4(N−1)]⁴`, here with `L = N − 1`. -/
theorem four_hull_subset_cube (L : ℝ) (X : Set (Fin 4 → ℝ))
    (hX : ∀ x ∈ X, ∀ i, 0 ≤ x i ∧ x i ≤ L) :
    ∀ x ∈ (4 : ℝ) • convexHull ℝ X, ∀ i, 0 ≤ x i ∧ x i ≤ 4 * L := by
  sorry

/-- Step 3 (eq:zeros). Fewer conditions than the dimension `∏ (b_j + 1)` leave a
nonzero `R` with `deg_{z_j} R ≤ b_j` vanishing at the given points. -/
theorem exists_vanishing (A : (Fin 4 → ℂ) →ₗ[ℂ] (Fin 3 → ℂ)) (b : Fin 3 → ℕ)
    (Z : Finset (Fin 4 → ℤ)) (hZ : Z.card < ∏ j, (b j + 1)) :
    ∃ R : MvPolynomial (Fin 3) ℂ, R ≠ 0 ∧ (∀ j, R.degreeOf j ≤ b j) ∧
      ∀ m ∈ Z, eval (A (zC m)) R = 0 := by
  sorry

/-- Step 4. `R ∘ A ≠ 0` (A is surjective) and a nonzero polynomial does not vanish on
all of `ℤ⁴`. -/
theorem exists_lattice_nonvanishing (A : (Fin 4 → ℂ) →ₗ[ℂ] (Fin 3 → ℂ))
    (hA : Function.Surjective A) (R : MvPolynomial (Fin 3) ℂ) (hR : R ≠ 0) :
    ∃ m : Fin 4 → ℤ, eval (A (zC m)) R ≠ 0 := by
  sorry

/-- Step 5 and the nearest-point inequality. Among the lattice points in `W`, one, `m`,
is at least distance from the compact convex set `K`; `y` is its nearest point in `K`.
(The distance from `m'` to `K` is the infimum of `sqd (zR m') z` over `z ∈ K`.) -/
theorem exists_nearest (K : Set (Fin 4 → ℝ)) (hKc : IsCompact K) (hKcv : Convex ℝ K)
    (hKne : K.Nonempty) (W : Set (Fin 4 → ℤ)) (hW : W.Nonempty) :
    ∃ m ∈ W, ∃ y ∈ K, (∀ x ∈ K, dotProduct (zR m - y) (x - y) ≤ 0) ∧
      ∀ m' ∈ W, ∀ z ∈ K, sqd (zR m) y ≤ sqd (zR m') z := by
  sorry

/-- Step 6. `y/4` lies in the face `G` of `P = conv S` maximizing `h·`. Here the face is
given by its points of `S`, so this also records the unstated fact that `G = conv(S ∩ G)`. -/
theorem quarter_mem_face {ι : Type*} (p : ι → Fin 4 → ℝ) (S : Finset ι) (h y : Fin 4 → ℝ)
    (hy : y ∈ (4 : ℝ) • convexHull ℝ (p '' S))
    (hmax : ∀ x ∈ (4 : ℝ) • convexHull ℝ (p '' S), dotProduct h (x - y) ≤ 0) :
    (1 / 4 : ℝ) • y ∈ convexHull ℝ
      (p '' {s | s ∈ S ∧ ∀ s' ∈ S, dotProduct h (p s') ≤ dotProduct h (p s)}) := by
  sorry

/-- Steps 7–8 (eq:vertex). A point of the hull of points lying in a hyperplane `h· = const`
(`h ≠ 0`, so affine dimension ≤ 3) is a combination of at most four of them, one with
coefficient ≥ 1/4; call it `u`. Then `4x − u ∈ 3·conv`. -/
theorem exists_heavy_vertex {ι : Type*} (p : ι → Fin 4 → ℝ) (T : Set ι) (h : Fin 4 → ℝ)
    (hh : h ≠ 0) (hT : ∀ s ∈ T, ∀ s' ∈ T, dotProduct h (p s) = dotProduct h (p s'))
    (x : Fin 4 → ℝ) (hx : x ∈ convexHull ℝ (p '' T)) :
    ∃ u ∈ T, (4 : ℝ) • x - p u ∈ (3 : ℝ) • convexHull ℝ (p '' T) := by
  sorry

/-- Steps 9–10 (eq:distance). With `m = y + h`, `y' = y + n − u ∈ 4P` and
`h·(u − n) > 0`, some point of `4P` is closer to `m' = m + n − u` than `y` is to `m`. -/
theorem closer_point (P : Set (Fin 4 → ℝ)) (hP : Convex ℝ P) (h y u n : Fin 4 → ℝ)
    (hyu : y - u ∈ (3 : ℝ) • P) (hn : n ∈ P) (hy : y ∈ (4 : ℝ) • P)
    (hpos : 0 < dotProduct h (u - n)) :
    ∃ z ∈ (4 : ℝ) • P, sqd (y + h + (n - u)) z < sqd (y + h) y := by
  sorry

/-- Step 12. Integer points on a real hyperplane `h· = const` (`h ≠ 0`) lie on an integer
hyperplane `r· = k`, `0 ≠ r ∈ ℤ⁴`. -/
theorem exists_int_hyperplane (T : Set (Fin 4 → ℤ)) (h : Fin 4 → ℝ) (hh : h ≠ 0)
    (hT : ∀ s ∈ T, ∀ s' ∈ T, dotProduct h (zR s) = dotProduct h (zR s')) :
    ∃ r : Fin 4 → ℤ, r ≠ 0 ∧ ∃ k : ℤ, ∀ s ∈ T, dotProduct r s = k := by
  sorry

/-- Step 12. Rational independence of the coordinates of `c` gives `r·c ≠ 0`. -/
theorem int_comb_ne_zero (c : Fin 4 → ℂ) (hc : LinearIndependent ℚ c) (r : Fin 4 → ℤ)
    (hr : r ≠ 0) : ∑ i, (r i : ℂ) * c i ≠ 0 := by
  sorry

/-- Steps 13–14. `A` restricted to `ℋ = {r·v = k}` is an affine bijection (`r·c ≠ 0`), so
there is a Lagrange polynomial `Q` of total degree ≤ `3(N−1)` equal to 1 at `Au` and 0 at
`An` for the other `n ∈ E_N ∩ ℋ` in `T`. -/
theorem exists_lagrange (A : (Fin 4 → ℂ) →ₗ[ℂ] (Fin 3 → ℂ)) (hA : Function.Surjective A)
    (c : Fin 4 → ℂ) (hker : LinearMap.ker A = Submodule.span ℂ {c}) (r : Fin 4 → ℤ)
    (hrc : ∑ i, (r i : ℂ) * c i ≠ 0) (k : ℤ) (N : ℕ) (T : Set (Fin 4 → Fin N))
    (hT : ∀ n ∈ T, dotProduct r (emb n) = k) (u : Fin 4 → Fin N) (hu : u ∈ T) :
    ∃ Q : MvPolynomial (Fin 3) ℂ, Q.totalDegree ≤ 3 * (N - 1) ∧
      eval (A (zC (emb u))) Q = 1 ∧ ∀ n ∈ T, n ≠ u → eval (A (zC (emb n))) Q = 0 := by
  sorry

/-- Step 15. Translation `z ↦ z + w` does not raise any separate degree. -/
theorem exists_translate (R : MvPolynomial (Fin 3) ℂ) (w : Fin 3 → ℂ) :
    ∃ R' : MvPolynomial (Fin 3) ℂ, (∀ j, R'.degreeOf j ≤ R.degreeOf j) ∧
      ∀ z, eval z R' = eval (z + w) R := by
  sorry

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

end

end Lemma3

#print Lemma3.Pt
#check @Lemma3.interpolation
#print axioms Lemma3.interpolation
