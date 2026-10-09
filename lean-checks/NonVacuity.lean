import Mathlib
import OAI.NumberTheory.SiegelZeros.Main

/-!
Non-vacuity checks for the challenge statement (docs/plan-remaining-gaps.md, step 4a).

A universally quantified statement is useless if its hypotheses can never hold.
Here we show that the hypotheses on `q` and `χ` in
`ComparatorChallenges/SiegelZeros.lean` hold for infinitely many characters (the
quadratic character mod every odd prime), that Mathlib's `LFunction` is the usual
Dirichlet series for `re s > 1`, and that the solution theorem specializes to them.

What this cannot show: that a real zero `β ∈ (0,1)` exists. None is known, and the
theorem is a statement about that (possibly empty) set of zeros.
-/

open DirichletCharacter

namespace NonVacuity

/-- The quadratic character mod a prime `p`, as a complex Dirichlet character. -/
noncomputable def quadChar (p : ℕ) [Fact p.Prime] : DirichletCharacter ℂ p :=
  (quadraticChar (ZMod p)).ringHomComp (Int.castRingHom ℂ)

lemma quadChar_apply (p : ℕ) [Fact p.Prime] (a : ZMod p) :
    quadChar p a = ((quadraticChar (ZMod p) a : ℤ) : ℂ) := rfl

/-- (i-a) It is real-valued. -/
lemma quadChar_real (p : ℕ) [Fact p.Prime] (a : ZMod p) : (quadChar p a).im = 0 := by
  rw [quadChar_apply]
  exact Complex.intCast_im _

/-- (i-b) It is not the trivial character, for `p ≠ 2`. -/
lemma quadChar_ne_one (p : ℕ) [Fact p.Prime] (hp : p ≠ 2) : quadChar p ≠ 1 := by
  intro h
  have hchar : ringChar (ZMod p) ≠ 2 := by rw [ZMod.ringChar_zmod_n]; exact hp
  obtain ⟨a, ha⟩ := quadraticChar_exists_neg_one hchar
  have ha0 : a ≠ 0 := by
    rintro rfl
    rw [quadraticChar_zero] at ha
    exact absurd ha (by decide)
  have hu : IsUnit a := isUnit_iff_ne_zero.mpr ha0
  have h1 := congrArg (fun χ : DirichletCharacter ℂ p => χ a) h
  simp only [quadChar_apply, ha, MulChar.one_apply hu] at h1
  norm_num at h1

/-- (i-c) It is primitive: its conductor divides the prime `p` and is not `1`. -/
lemma quadChar_isPrimitive (p : ℕ) [hp : Fact p.Prime] (h2 : p ≠ 2) :
    (quadChar p).IsPrimitive := by
  have : NeZero p := ⟨hp.out.ne_zero⟩
  rw [isPrimitive_def]
  rcases (Nat.dvd_prime hp.out).1 (conductor_dvd_level (quadChar p)) with h | h
  · exact absurd (eq_one_iff_conductor_eq_one.2 h) (quadChar_ne_one p h2)
  · exact h

/-- (i) Every hypothesis of the challenge statement on `q` and `χ` holds for the
quadratic character mod any odd prime. -/
theorem hypotheses_satisfiable (p : ℕ) [hp : Fact p.Prime] (h2 : p ≠ 2) :
    3 ≤ p ∧ (quadChar p).IsPrimitive ∧ quadChar p ≠ 1 ∧
      ∀ a : ZMod p, (quadChar p a).im = 0 := by
  refine ⟨?_, quadChar_isPrimitive p h2, quadChar_ne_one p h2, quadChar_real p⟩
  have := hp.out.two_le
  omega

instance : Fact (Nat.Prime 3) := ⟨by norm_num⟩
instance : Fact (Nat.Prime 5) := ⟨by norm_num⟩

example : 3 ≤ 3 ∧ (quadChar 3).IsPrimitive ∧ quadChar 3 ≠ 1 ∧
    ∀ a : ZMod 3, (quadChar 3 a).im = 0 := hypotheses_satisfiable 3 (by norm_num)

example : 3 ≤ 5 ∧ (quadChar 5).IsPrimitive ∧ quadChar 5 ≠ 1 ∧
    ∀ a : ZMod 5, (quadChar 5 a).im = 0 := hypotheses_satisfiable 5 (by norm_num)

/-- (ii) `LFunction` is the Dirichlet series `∑ χ(n) n^{-s}` for `re s > 1`. -/
theorem quadChar_LFunction_eq_LSeries (p : ℕ) [Fact p.Prime] {s : ℂ} (hs : 1 < s.re) :
    (quadChar p).LFunction s = LSeries (fun n => quadChar p n) s :=
  LFunction_eq_LSeries _ hs

/-- (ii) and it does not vanish at `s = 1`, so it is not degenerate there. -/
theorem quadChar_LFunction_one_ne_zero (p : ℕ) [Fact p.Prime] (h2 : p ≠ 2) :
    (quadChar p).LFunction 1 ≠ 0 :=
  LFunction_ne_zero_of_one_le_re _ (Or.inl (quadChar_ne_one p h2)) (by simp)

/-- (iii) The solution theorem, specialized to these characters. -/
theorem specialization : ∃ c : ℝ, 0 < c ∧ ∀ (p : ℕ) [Fact p.Prime], p ≠ 2 →
    ∀ β : ℝ, 0 < β → β < 1 → (quadChar p).LFunction (β : ℂ) = 0 →
      c ≤ (1 - β) * Real.log (p : ℝ) := by
  obtain ⟨c, hc, h⟩ := OAI.SiegelZeros.WeightedTorusJets.exists_absolute_real_zero_gap
  refine ⟨c, hc, fun p hp h2 β h0 h1 hz => ?_⟩
  have : NeZero p := ⟨hp.out.ne_zero⟩
  obtain ⟨h3, hprim, hne, hreal⟩ := hypotheses_satisfiable p h2
  exact h p h3 (quadChar p) hprim hne hreal β h0 h1 hz

end NonVacuity

#print axioms NonVacuity.hypotheses_satisfiable
#print axioms NonVacuity.quadChar_LFunction_eq_LSeries
#print axioms NonVacuity.quadChar_LFunction_one_ne_zero
#print axioms NonVacuity.specialization
