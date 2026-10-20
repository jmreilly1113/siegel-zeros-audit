import StatementChecks.Challenges.HeckeSevenEighths

/-! Statement check 5c, first half (time-boxed attempt): the challenge's `LFunction χ s`, defined through
a theta-function Mellin transform, equals the lattice Dirichlet series
`(1/6) ∑_{(x,y) ≠ 0} χ(x + y ω) / (x² - x y + y²)^s` for `re s > 1`.

Uses the challenge-side definitions only (no solution module). -/

open OAI.SevenEighths OAI.SevenEighths.HeckeFamily OAI.SevenEighths.HeckeTheta
  OAI.SevenEighths.EisensteinTheta OAI.SevenEighths.ThetaProduct
open Real Filter Set

namespace StatementChecks.HeckeSeries

variable (χ : Character)

/-- The norm form of `x + y ω`. -/
def Qf (x y : ℤ) : ℤ := x ^ 2 - x * y + y ^ 2

/-- The coefficient attached to the lattice point `(x, y)`, i.e. `χ (x + y ω)`. -/
noncomputable def c (x y : ℤ) : ℂ := elementCoeff χ (coordinateElement x y)

lemma c_periodic (x y k l : ℤ) :
    c χ (x + χ.period * k) (y + χ.period * l) = c χ x y := by
  unfold c elementCoeff
  congr 1
  rw [Ideal.Quotient.eq]
  have h : coordinateElement (x + χ.period * k) (y + χ.period * l) - coordinateElement x y =
      (χ.period : O) * ((k : O) + (l : O) * omega) := by
    simp only [coordinateElement]; push_cast; ring
  rw [h]
  exact Ideal.mul_mem_right _ _ χ.period_mem

lemma coefficients_eq (a b : Fin χ.period) : coefficients χ (a, b) = c χ a b := rfl

/-! ### One component of the theta pair as a double sum -/

lemma parityPair_f (a b L : ℝ) (hL : 0 < L) (e : Fin 2) (t : ℝ) :
    (parityPair a b L hL e).f t =
      ((HurwitzZeta.evenKernel (xShift a b L e) (L ^ 2 * t) : ℝ) : ℂ) *
      ((HurwitzZeta.evenKernel (yShift b L e) (3 * L ^ 2 * t) : ℝ) : ℂ) := rfl

lemma hasSum_component (a b L : ℝ) (hL : 0 < L) (e : Fin 2) {t : ℝ} (ht : 0 < t) :
    HasSum (fun mn : ℤ × ℤ =>
      ((rexp (-π * (mn.1 + xShift a b L e) ^ 2 * (L ^ 2 * t)) *
        rexp (-π * (mn.2 + yShift b L e) ^ 2 * (3 * L ^ 2 * t)) : ℝ) : ℂ))
      ((parityPair a b L hL e).f t) := by
  have h1 := HurwitzZeta.hasSum_int_evenKernel (xShift a b L e) (by positivity : 0 < L ^ 2 * t)
  have h2 := HurwitzZeta.hasSum_int_evenKernel (yShift b L e) (by positivity : 0 < 3 * L ^ 2 * t)
  have hs : Summable fun mn : ℤ × ℤ =>
      rexp (-π * (mn.1 + xShift a b L e) ^ 2 * (L ^ 2 * t)) *
        rexp (-π * (mn.2 + yShift b L e) ^ 2 * (3 * L ^ 2 * t)) :=
    summable_mul_of_summable_norm (f := fun m : ℤ => rexp (-π * (m + xShift a b L e) ^ 2 * (L ^ 2 * t)))
      (g := fun n : ℤ => rexp (-π * (n + yShift b L e) ^ 2 * (3 * L ^ 2 * t)))
      (by simpa [Real.norm_eq_abs, abs_of_pos (Real.exp_pos _)] using h1.summable)
      (by simpa [Real.norm_eq_abs, abs_of_pos (Real.exp_pos _)] using h2.summable)
  have h := h1.mul h2 hs
  rw [parityPair_f]
  rw [← Complex.ofReal_mul]
  exact (Complex.hasSum_ofReal).mpr h

/-! ### The explicit bijection `(residues, parity) × ℤ² ≃ ℤ²` -/

section Bij

variable (N : ℕ) [NeZero N]

/-- `((a, b), e), (m, n) ↦ (N (m + n) + a, b + N (2 n + e))`. -/
def Φf (p : ((Fin N × Fin N) × Fin 2) × (ℤ × ℤ)) : ℤ × ℤ :=
  ((N : ℤ) * (p.2.1 + p.2.2) + (p.1.1.1 : ℕ), ((p.1.1.2 : ℕ) : ℤ) + N * (2 * p.2.2 + (p.1.2 : ℕ)))

lemma Npos : (0 : ℤ) < N := by exact_mod_cast NeZero.pos N

/-- The inverse. -/
def Ψf (q : ℤ × ℤ) : ((Fin N × Fin N) × Fin 2) × (ℤ × ℤ) :=
  let bq := q.2 % N; let qq := q.2 / N; let e := qq % 2; let n := qq / 2
  let a := q.1 % N; let m := q.1 / N - n
  (((⟨a.toNat, by have := Int.emod_lt_of_pos q.1 (Npos N); have := Int.emod_nonneg q.1 (Npos N).ne'; omega⟩,
     ⟨bq.toNat, by have := Int.emod_lt_of_pos q.2 (Npos N); have := Int.emod_nonneg q.2 (Npos N).ne'; omega⟩),
    ⟨e.toNat, by have := Int.emod_lt_of_pos qq (by norm_num : (0 : ℤ) < 2); have := Int.emod_nonneg qq (by norm_num : (2 : ℤ) ≠ 0); omega⟩),
   (m, n))

lemma Φf_Ψf (q : ℤ × ℤ) : Φf N (Ψf N q) = q := by
  obtain ⟨X, y⟩ := q
  have hN := Npos N
  have h1 := Int.emod_nonneg X hN.ne'; have h2 := Int.emod_nonneg y hN.ne'
  have h3 := Int.emod_nonneg (y / N) (by norm_num : (2 : ℤ) ≠ 0)
  simp only [Φf, Ψf, Prod.mk.injEq]
  constructor
  · rw [Int.toNat_of_nonneg h1]
    have := Int.emod_add_mul_ediv X N
    linarith
  · rw [Int.toNat_of_nonneg h2, Int.toNat_of_nonneg h3]
    have e1 := Int.emod_add_mul_ediv y N
    have e2 := Int.emod_add_mul_ediv (y / N) 2
    nlinarith

lemma Ψf_Φf (p : ((Fin N × Fin N) × Fin 2) × (ℤ × ℤ)) : Ψf N (Φf N p) = p := by
  obtain ⟨⟨⟨a, b⟩, e⟩, ⟨m, n⟩⟩ := p
  have hN := Npos N
  have ha : ((a : ℕ) : ℤ) < N := by exact_mod_cast a.isLt
  have hb : ((b : ℕ) : ℤ) < N := by exact_mod_cast b.isLt
  have he : ((e : ℕ) : ℤ) < 2 := by exact_mod_cast e.isLt
  have ha0 : (0 : ℤ) ≤ (a : ℕ) := by positivity
  have hb0 : (0 : ℤ) ≤ (b : ℕ) := by positivity
  have he0 : (0 : ℤ) ≤ (e : ℕ) := by positivity
  -- y = b + N q with q = 2 n + e, X = a + N (m + n)
  have hy_mod : (((b : ℕ) : ℤ) + N * (2 * n + (e : ℕ))) % N = (b : ℕ) := by
    rw [Int.add_mul_emod_self_left]; exact Int.emod_eq_of_lt hb0 hb
  have hy_div : (((b : ℕ) : ℤ) + N * (2 * n + (e : ℕ))) / N = 2 * n + (e : ℕ) := by
    rw [Int.add_mul_ediv_left _ _ hN.ne', Int.ediv_eq_zero_of_lt hb0 hb, zero_add]
  have hq_mod : (2 * n + ((e : ℕ) : ℤ)) % 2 = (e : ℕ) := by
    rw [add_comm, Int.add_mul_emod_self_left]; exact Int.emod_eq_of_lt he0 he
  have hq_div : (2 * n + ((e : ℕ) : ℤ)) / 2 = n := by
    rw [add_comm, Int.add_mul_ediv_left _ _ (by norm_num), Int.ediv_eq_zero_of_lt he0 he, zero_add]
  have hX_mod : ((N : ℤ) * (m + n) + (a : ℕ)) % N = (a : ℕ) := by
    rw [add_comm, Int.add_mul_emod_self_left]; exact Int.emod_eq_of_lt ha0 ha
  have hX_div : ((N : ℤ) * (m + n) + (a : ℕ)) / N = m + n := by
    rw [add_comm, Int.add_mul_ediv_left _ _ hN.ne', Int.ediv_eq_zero_of_lt ha0 ha, zero_add]
  simp only [Φf, Ψf, hy_mod, hy_div, hq_mod, hq_div, hX_mod, hX_div, Int.toNat_natCast,
    add_sub_cancel_right]

/-- The bijection as an `Equiv`. -/
def Φ : ((Fin N × Fin N) × Fin 2) × (ℤ × ℤ) ≃ ℤ × ℤ where
  toFun := Φf N
  invFun := Ψf N
  left_inv := Ψf_Φf N
  right_inv := Φf_Ψf N

end Bij

/-! ### The exponent and the weights along the bijection -/

lemma exponent_eq (N : ℕ) [NeZero N] (a b : Fin N) (e : Fin 2) (m n : ℤ) (t : ℝ) :
    -π * (m + xShift (a : ℕ) (b : ℕ) N e) ^ 2 * ((N : ℝ) ^ 2 * t) +
      -π * (n + yShift (b : ℕ) N e) ^ 2 * (3 * (N : ℝ) ^ 2 * t) =
    -π * ((Qf (Φf N (((a, b), e), (m, n))).1 (Φf N (((a, b), e), (m, n))).2 : ℤ) : ℝ) * t := by
  have hN : (N : ℝ) ≠ 0 := by exact_mod_cast (NeZero.ne N)
  simp only [xShift, yShift, Qf, Φf]
  push_cast
  field_simp
  ring

lemma weight_eq (a b : Fin χ.period) (e : Fin 2) (m n : ℤ) :
    coefficients χ (a, b) =
      c χ (Φf χ.period (((a, b), e), (m, n))).1 (Φf χ.period (((a, b), e), (m, n))).2 := by
  rw [coefficients_eq]
  simp only [Φf]
  have := c_periodic χ ((a : ℕ) : ℤ) ((b : ℕ) : ℤ) (m + n) (2 * n + (e : ℕ))
  rw [← this]
  congr 1 <;> ring

/-! ### `pair.f t` as a sum over the lattice -/

lemma pair_f_apply (t : ℝ) :
    (pair (coefficients χ)).f t =
      ∑ p : (Fin χ.period × Fin χ.period) × Fin 2,
        coefficients χ p.1 * (parityPair (p.1.1 : ℕ) (p.1.2 : ℕ) χ.period
          (Nat.cast_pos.mpr (NeZero.pos χ.period)) p.2).f t := by
  simp [pair, finitePair, Finset.sum_apply, smul_eq_mul]

/-- The family on `(residues, parity) × ℤ²` whose fibres are the components. -/
noncomputable def Fam (t : ℝ) (p : ((Fin χ.period × Fin χ.period) × Fin 2) × (ℤ × ℤ)) : ℂ :=
  coefficients χ p.1.1 *
    ((rexp (-π * (p.2.1 + xShift (p.1.1.1 : ℕ) (p.1.1.2 : ℕ) χ.period p.1.2) ^ 2 * ((χ.period : ℝ) ^ 2 * t)) *
      rexp (-π * (p.2.2 + yShift (p.1.1.2 : ℕ) χ.period p.1.2) ^ 2 * (3 * (χ.period : ℝ) ^ 2 * t)) : ℝ) : ℂ)

lemma Fam_eq (t : ℝ) (p : ((Fin χ.period × Fin χ.period) × Fin 2) × (ℤ × ℤ)) :
    Fam χ t p = c χ (Φf χ.period p).1 (Φf χ.period p).2 *
      ((rexp (-π * (Qf (Φf χ.period p).1 (Φf χ.period p).2 : ℝ) * t) : ℝ) : ℂ) := by
  obtain ⟨⟨⟨a, b⟩, e⟩, ⟨m, n⟩⟩ := p
  unfold Fam
  rw [← weight_eq χ a b e m n, ← Real.exp_add, exponent_eq]

lemma hasSum_Fam_fibre (t : ℝ) (ht : 0 < t) (p0 : (Fin χ.period × Fin χ.period) × Fin 2) :
    HasSum (fun mn => Fam χ t (p0, mn))
      (coefficients χ p0.1 * (parityPair (p0.1.1 : ℕ) (p0.1.2 : ℕ) χ.period
        (Nat.cast_pos.mpr (NeZero.pos χ.period)) p0.2).f t) := by
  have h := (hasSum_component ((p0.1.1 : ℕ) : ℝ) ((p0.1.2 : ℕ) : ℝ) (χ.period : ℝ)
    (Nat.cast_pos.mpr (NeZero.pos χ.period)) p0.2 ht).mul_left (coefficients χ p0.1)
  refine h.congr_fun ?_
  intro mn
  rfl

lemma hasSum_pair_f {t : ℝ} (ht : 0 < t) :
    HasSum (fun q : ℤ × ℤ => c χ q.1 q.2 * ((rexp (-π * (Qf q.1 q.2 : ℝ) * t) : ℝ) : ℂ))
      ((pair (coefficients χ)).f t) := by
  have hsumm : Summable (Fam χ t) := by
    apply Summable.of_norm
    rw [summable_prod_of_nonneg (fun _ => norm_nonneg _)]
    exact ⟨fun p0 => (hasSum_Fam_fibre χ t ht p0).summable.norm, Summable.of_finite⟩
  have hfib := hsumm.hasSum.prod_fiberwise (hasSum_Fam_fibre χ t ht)
  have hfin := hasSum_fintype (fun p0 : (Fin χ.period × Fin χ.period) × Fin 2 =>
      coefficients χ p0.1 * (parityPair (p0.1.1 : ℕ) (p0.1.2 : ℕ) χ.period
        (Nat.cast_pos.mpr (NeZero.pos χ.period)) p0.2).f t)
  have hF : HasSum (Fam χ t) ((pair (coefficients χ)).f t) := by
    rw [pair_f_apply, ← hfib.unique hfin]
    exact hsumm.hasSum
  refine (Φ χ.period).hasSum_iff.mp ?_
  have hfun : ((fun q : ℤ × ℤ => c χ q.1 q.2 * ((rexp (-π * (Qf q.1 q.2 : ℝ) * t) : ℝ) : ℂ)) ∘
      (Φ χ.period)) = Fam χ t := by
    funext p
    rw [Function.comp_apply, Fam_eq]
    rfl
  rw [hfun]
  exact hF

/-! ### The constant term `f₀` -/

lemma parityPair_f₀ (a b L : ℝ) (hL : 0 < L) (e : Fin 2) :
    (parityPair a b L hL e).f₀ =
      (if ((xShift a b L e : ℝ) : UnitAddCircle) = 0 then 1 else 0) *
      (if ((yShift b L e : ℝ) : UnitAddCircle) = 0 then 1 else 0) := rfl

lemma yShift_mem (N : ℕ) [NeZero N] (b : Fin N) (e : Fin 2) :
    yShift (b : ℕ) N e ∈ Ico (0 : ℝ) 1 := by
  have hN : (0 : ℝ) < N := Nat.cast_pos.mpr (NeZero.pos N)
  have hb : ((b : ℕ) : ℝ) < N := by exact_mod_cast b.isLt
  have he : ((e : ℕ) : ℝ) ≤ 1 := by exact_mod_cast Nat.lt_succ_iff.mp e.isLt
  simp only [yShift, mem_Ico]
  constructor
  · positivity
  · rw [div_lt_one (by positivity)]; nlinarith

lemma coe_yShift_eq_zero (N : ℕ) [NeZero N] (b : Fin N) (e : Fin 2) :
    ((yShift (b : ℕ) N e : ℝ) : UnitAddCircle) = 0 ↔ (b : ℕ) = 0 ∧ (e : ℕ) = 0 := by
  rw [AddCircle.coe_eq_zero_iff_of_mem_Ico (yShift_mem N b e)]
  have hN : (0 : ℝ) < N := Nat.cast_pos.mpr (NeZero.pos N)
  simp only [yShift, div_eq_zero_iff]
  constructor
  · rintro (h | h)
    · have hb : (0 : ℝ) ≤ (b : ℕ) := by positivity
      have he : (0 : ℝ) ≤ (e : ℕ) := by positivity
      have h1 : ((b : ℕ) : ℝ) = 0 := by nlinarith
      have h2 : ((e : ℕ) : ℝ) = 0 := by nlinarith
      exact ⟨by exact_mod_cast h1, by exact_mod_cast h2⟩
    · exfalso; linarith
  · rintro ⟨h1, h2⟩; left; simp [h1, h2]

lemma coe_xShift_zero_eq_zero (N : ℕ) [NeZero N] (a : Fin N) :
    ((xShift (a : ℕ) ((0 : Fin N) : ℕ) N (0 : Fin 2) : ℝ) : UnitAddCircle) = 0 ↔ (a : ℕ) = 0 := by
  have hN : (0 : ℝ) < N := Nat.cast_pos.mpr (NeZero.pos N)
  have ha : ((a : ℕ) : ℝ) < N := by exact_mod_cast a.isLt
  have hmem : xShift (a : ℕ) ((0 : Fin N) : ℕ) N (0 : Fin 2) ∈ Ico (0 : ℝ) 1 := by
    simp only [xShift, Fin.val_zero, Nat.cast_zero, mul_zero, sub_zero, mem_Ico]
    constructor
    · positivity
    · rw [div_lt_one (by positivity)]; linarith
  rw [AddCircle.coe_eq_zero_iff_of_mem_Ico hmem]
  simp only [xShift, Fin.val_zero, Nat.cast_zero, mul_zero, sub_zero, div_eq_zero_iff]
  constructor
  · rintro (h | h)
    · exact_mod_cast (by linarith : ((a : ℕ) : ℝ) = 0)
    · exfalso; linarith
  · intro h; left; simp [h]

lemma pair_f₀ : (pair (coefficients χ)).f₀ = c χ 0 0 := by
  have hsum : (pair (coefficients χ)).f₀ =
      ∑ p : (Fin χ.period × Fin χ.period) × Fin 2, coefficients χ p.1 *
        (parityPair (p.1.1 : ℕ) (p.1.2 : ℕ) χ.period (Nat.cast_pos.mpr (NeZero.pos χ.period)) p.2).f₀ := by
    simp [pair, finitePair]
  rw [hsum]
  have hterm : ∀ p : (Fin χ.period × Fin χ.period) × Fin 2, coefficients χ p.1 *
      (parityPair (p.1.1 : ℕ) (p.1.2 : ℕ) χ.period (Nat.cast_pos.mpr (NeZero.pos χ.period)) p.2).f₀ =
      if p = ((0, 0), 0) then coefficients χ ((0, 0)) else 0 := by
    rintro ⟨⟨a, b⟩, e⟩
    rw [parityPair_f₀]
    by_cases hbe : (b : ℕ) = 0 ∧ (e : ℕ) = 0
    · have hb : b = 0 := Fin.ext hbe.1
      have he : e = 0 := Fin.ext hbe.2
      subst hb he
      by_cases ha : (a : ℕ) = 0
      · have ha' : a = 0 := Fin.ext ha
        subst ha'
        rw [if_pos ((coe_xShift_zero_eq_zero χ.period 0).mpr rfl),
          if_pos ((coe_yShift_eq_zero χ.period 0 0).mpr ⟨rfl, rfl⟩), if_pos rfl, mul_one, mul_one]
      · have hx : ¬ ((xShift (a : ℕ) ((0 : Fin χ.period) : ℕ) χ.period (0 : Fin 2) : ℝ) : UnitAddCircle) = 0 :=
          fun h => ha ((coe_xShift_zero_eq_zero χ.period a).mp h)
        have hne : ((a, (0 : Fin χ.period)), (0 : Fin 2)) ≠ ((0, 0), 0) := by
          intro h; apply ha; simp only [Prod.mk.injEq] at h; rw [h.1.1]; rfl
        rw [if_neg hx, if_neg hne, zero_mul, mul_zero]
    · have hy : ¬ ((yShift (b : ℕ) χ.period e : ℝ) : UnitAddCircle) = 0 :=
        fun h => hbe ((coe_yShift_eq_zero χ.period b e).mp h)
      have hne : ((a, b), e) ≠ ((0, 0), 0) := by
        intro h; apply hbe; simp only [Prod.mk.injEq] at h; rw [h.1.2, h.2]; exact ⟨rfl, rfl⟩
      rw [if_neg hy, if_neg hne, mul_zero, mul_zero]
  rw [Finset.sum_congr rfl (fun p _ => hterm p), Finset.sum_ite_eq']
  simp [coefficients_eq]

/-! ### Summability of the lattice Dirichlet series -/

/-- A bound for all coefficients: they take only the finitely many values of `coefficients χ`. -/
noncomputable def M : ℝ := ∑ p : Fin χ.period × Fin χ.period, ‖coefficients χ p‖

lemma norm_c_le (x y : ℤ) : ‖c χ x y‖ ≤ M χ := by
  have h := Φf_Ψf χ.period (x, y)
  rcases hΨ : Ψf χ.period (x, y) with ⟨⟨⟨a, b⟩, e⟩, ⟨m, n⟩⟩
  rw [hΨ] at h
  have hx : x = (Φf χ.period (((a, b), e), (m, n))).1 := by rw [h]
  have hy : y = (Φf χ.period (((a, b), e), (m, n))).2 := by rw [h]
  rw [hx, hy, ← weight_eq χ a b e m n]
  exact Finset.single_le_sum (f := fun p => ‖coefficients χ p‖) (fun _ _ => norm_nonneg _)
    (Finset.mem_univ (a, b))

lemma M_nonneg : 0 ≤ M χ := Finset.sum_nonneg (fun _ _ => norm_nonneg _)

lemma Qf_ge (x y : ℤ) : ((x : ℝ) ^ 2 + (y : ℝ) ^ 2) / 2 ≤ (Qf x y : ℝ) := by
  simp only [Qf]; push_cast; nlinarith [sq_nonneg ((x : ℝ) - y)]

lemma Qf_nonneg (x y : ℤ) : 0 ≤ (Qf x y : ℝ) := le_trans (by positivity) (Qf_ge x y)

lemma Qf_pos {x y : ℤ} (h : (x, y) ≠ 0) : 0 < (Qf x y : ℝ) := by
  have : (x : ℝ) ≠ 0 ∨ (y : ℝ) ≠ 0 := by
    by_contra hc; push_neg at hc; apply h
    simp only [Prod.mk_eq_zero]; exact ⟨by exact_mod_cast hc.1, by exact_mod_cast hc.2⟩
  have hpos : 0 < (x : ℝ) ^ 2 + (y : ℝ) ^ 2 := by
    rcases this with h1 | h1
    · have := pow_pos (abs_pos.mpr h1) 2; rw [sq_abs] at this; nlinarith [sq_nonneg (y : ℝ)]
    · have := pow_pos (abs_pos.mpr h1) 2; rw [sq_abs] at this; nlinarith [sq_nonneg (x : ℝ)]
  linarith [Qf_ge x y]

/-- The coefficient with the `(0,0)` term removed. -/
noncomputable def a' (q : ℤ × ℤ) : ℂ := if q = 0 then 0 else c χ q.1 q.2

lemma summable_lattice {σ : ℝ} (hσ : 1 < σ) :
    Summable fun q : ℤ × ℤ => ‖a' χ q‖ / (π * (Qf q.1 q.2 : ℝ)) ^ σ := by
  rw [← (finTwoArrowEquiv ℤ).summable_iff]
  have hk : 2 < 2 * σ := by linarith
  refine ((EisensteinSeries.summable_one_div_norm_rpow hk).mul_left (M χ * (π / 2) ^ (-σ))).of_nonneg_of_le
    (fun v => div_nonneg (norm_nonneg _)
      (Real.rpow_nonneg (mul_nonneg Real.pi_pos.le (Qf_nonneg _ _)) _)) ?_
  intro v
  change ‖a' χ (v 0, v 1)‖ / (π * ((Qf (v 0) (v 1) : ℤ) : ℝ)) ^ σ ≤ M χ * (π / 2) ^ (-σ) * ‖v‖ ^ (-(2 * σ))
  by_cases hv : (v 0, v 1) = 0
  · rw [show a' χ (v 0, v 1) = 0 by simp [a', hv], norm_zero, zero_div]
    exact mul_nonneg (mul_nonneg (M_nonneg χ) (Real.rpow_nonneg (by positivity) _))
      (Real.rpow_nonneg (norm_nonneg _) _)
  · have hv' : v ≠ 0 := by
      intro h0; apply hv; simp [h0]
    have hQ := Qf_pos hv
    have hnorm_pos : 0 < ‖v‖ := norm_pos_iff.mpr hv'
    -- ‖v‖^2 ≤ (v 0)^2 + (v 1)^2 ≤ 2 Q
    have hnorm_sq : ‖v‖ ^ 2 ≤ ((v 0 : ℝ) ^ 2 + (v 1 : ℝ) ^ 2) := by
      have hle : ‖v‖ ≤ Real.sqrt ((v 0 : ℝ) ^ 2 + (v 1 : ℝ) ^ 2) := by
        refine (pi_norm_le_iff_of_nonneg (Real.sqrt_nonneg _)).mpr ?_
        intro i
        rw [Int.norm_eq_abs, ← Real.sqrt_sq_eq_abs]
        apply Real.sqrt_le_sqrt
        fin_cases i
        · simp; nlinarith [sq_nonneg ((v 1 : ℤ) : ℝ)]
        · simp; nlinarith [sq_nonneg ((v 0 : ℤ) : ℝ)]
      calc ‖v‖ ^ 2 ≤ (Real.sqrt ((v 0 : ℝ) ^ 2 + (v 1 : ℝ) ^ 2)) ^ 2 := by gcongr
        _ = _ := Real.sq_sqrt (by positivity)
    have hbase : π / 2 * ‖v‖ ^ 2 ≤ π * (Qf (v 0) (v 1) : ℝ) := by
      have := Qf_ge (v 0) (v 1)
      nlinarith [Real.pi_pos]
    have h1 : ‖a' χ (v 0, v 1)‖ ≤ M χ := by
      simp only [a', if_neg hv]; exact norm_c_le χ _ _
    have h2 : (π / 2 * ‖v‖ ^ 2) ^ σ ≤ (π * (Qf (v 0) (v 1) : ℝ)) ^ σ :=
      Real.rpow_le_rpow (by positivity) hbase (by linarith)
    have h3 : 0 < (π / 2 * ‖v‖ ^ 2) ^ σ := by positivity
    calc ‖a' χ (v 0, v 1)‖ / (π * (Qf (v 0) (v 1) : ℝ)) ^ σ
        ≤ M χ / (π / 2 * ‖v‖ ^ 2) ^ σ := by
          apply div_le_div₀ (M_nonneg χ) h1 h3 h2
      _ = M χ * (π / 2) ^ (-σ) * ‖v‖ ^ (-(2 * σ)) := by
          rw [Real.mul_rpow (by positivity) (by positivity), Real.rpow_neg (by positivity),
            Real.rpow_neg (by positivity), ← Real.rpow_natCast, ← Real.rpow_mul (norm_nonneg _)]
          push_cast
          field_simp

/-! ### Main result: the defined L-function is the lattice Dirichlet series for `re s > 1` -/

theorem LFunction_hasSum {s : ℂ} (hs : 1 < s.re) :
    HasSum (fun q : ℤ × ℤ => a' χ q / ((Qf q.1 q.2 : ℝ) : ℂ) ^ s / 6) (LFunction χ s) := by
  have hs0 : 0 < s.re := by linarith
  -- the theta function minus its constant term, as a sum over the lattice
  have hF : ∀ t ∈ Ioi (0 : ℝ), HasSum (fun q : ℤ × ℤ => a' χ q * rexp (-(π * (Qf q.1 q.2 : ℝ)) * t))
      ((pair (coefficients χ)).f t - (pair (coefficients χ)).f₀) := by
    intro t ht
    have h := (hasSum_pair_f χ ht).update (0 : ℤ × ℤ) 0
    have hval : (0 : ℂ) - c χ (0 : ℤ × ℤ).1 (0 : ℤ × ℤ).2 * ((rexp (-π * (Qf (0 : ℤ × ℤ).1 (0 : ℤ × ℤ).2 : ℝ) * t) : ℝ) : ℂ) +
        (pair (coefficients χ)).f t = (pair (coefficients χ)).f t - (pair (coefficients χ)).f₀ := by
      rw [pair_f₀]; simp [Qf]; ring
    rw [hval] at h
    convert h using 1
    funext q
    by_cases hq : q = 0
    · subst hq; simp [a']
    · rw [Function.update_of_ne hq]; simp only [a', if_neg hq]; push_cast; ring_nf
  have hp : ∀ q : ℤ × ℤ, a' χ q = 0 ∨ 0 < π * (Qf q.1 q.2 : ℝ) := by
    intro q
    by_cases hq : q = 0
    · left; simp [a', hq]
    · right; exact mul_pos Real.pi_pos (Qf_pos (by simpa using hq))
  have hMel := hasSum_mellin hp hs0 hF (summable_lattice χ hs)
  have hΛ : mellin (fun t => (pair (coefficients χ)).f t - (pair (coefficients χ)).f₀) s =
      (pair (coefficients χ)).Λ s := by
    have hk : (pair (coefficients χ)).k = 1 := rfl
    exact ((pair (coefficients χ)).hasMellin (by rw [hk]; exact hs)).2
  rw [hΛ] at hMel
  have hL : LFunction χ s = (Real.pi : ℂ) ^ s * (Complex.Gamma s)⁻¹ * (pair (coefficients χ)).Λ s / 6 := rfl
  rw [hL]
  have h2 := (hMel.mul_left ((Real.pi : ℂ) ^ s * (Complex.Gamma s)⁻¹)).div_const 6
  convert h2 using 1
  funext q
  have hG : Complex.Gamma s ≠ 0 := Complex.Gamma_ne_zero_of_re_pos hs0
  by_cases hq : q = 0
  · simp [a', hq]
  · have hQ := Qf_pos (x := q.1) (y := q.2) (by simpa using hq)
    have hpi : (Real.pi : ℂ) ^ s ≠ 0 := by
      rw [Ne, Complex.cpow_eq_zero_iff]; push_neg
      intro h; exact absurd h (Complex.ofReal_ne_zero.mpr Real.pi_ne_zero)
    have hQc : ((Qf q.1 q.2 : ℝ) : ℂ) ^ s ≠ 0 := by
      rw [Ne, Complex.cpow_eq_zero_iff]; push_neg
      intro h; exact absurd h (Complex.ofReal_ne_zero.mpr hQ.ne')
    rw [Complex.ofReal_mul, Complex.mul_cpow_ofReal_nonneg Real.pi_pos.le hQ.le]
    field_simp

end StatementChecks.HeckeSeries

#print axioms StatementChecks.HeckeSeries.hasSum_pair_f
#print axioms StatementChecks.HeckeSeries.pair_f₀
#print axioms StatementChecks.HeckeSeries.LFunction_hasSum
