import Lemma3Bridged

/-!
# The main theorem, rerouted through the paper's Lemma 3

`Lemma3Bridged` proves OAI's exact Corollary 4 statement
(`OAI.SiegelZeros.WeightedTorusJets.actual_biquadratic_rectangle_span`) by the paper's route
(Lemma 3 → Corollary 4), as `Lemma3.actual_biquadratic_rectangle_span_via_lemma3`.

This file does not edit OAI's sources (rule 7). Instead `#reroute` takes OAI's already-elaborated
proof terms and makes a copy, under the prefix `Rerouted.`, of every constant in the main theorem's
dependency closure that (transitively) uses OAI's Corollary 4. In each copy, every reference to OAI's
Corollary 4 is replaced by our theorem, and every reference to another rerouted constant by its copy.
Each copy is sent to Lean's kernel with `addDecl`, so it is type-checked again from scratch.

Nothing else changes: the copies are OAI's proofs, term for term, with one lemma swapped.
-/

open Lean Elab Command

/-- `#reroute old new pre [roots]`: copy every constant in the closure of `roots` that transitively
references `old`, under prefix `pre`, with `old ↦ new`, and add the copies to the environment
(kernel-checked). -/
elab "#reroute " old:ident new:ident pre:ident " [" roots:ident,* "]" : command => do
  let env ← getEnv
  let old ← liftCoreM <| realizeGlobalConstNoOverloadWithInfo old
  let new ← liftCoreM <| realizeGlobalConstNoOverloadWithInfo new
  let pre := pre.getId
  let roots ← roots.getElems.toList.mapM fun r =>
    liftCoreM <| realizeGlobalConstNoOverloadWithInfo r
  let refsOf (c : Name) : Array Name := match env.find? c with
    | some ci =>
      let v : Option Expr := match ci with
        | .thmInfo t => some t.value
        | .defnInfo d => some d.value
        | .opaqueInfo o => some o.value
        | _ => none
      ci.type.getUsedConstants ++ (v.map (·.getUsedConstants) |>.getD #[])
    | none => #[]
  -- iterative post-order DFS; `order` lists constants with dependencies first
  let mut done : NameSet := {}
  let mut onStack : NameSet := {}
  let mut order : Array Name := #[]
  let mut stack : List (Name × Bool) := roots.map (·, false)
  while !stack.isEmpty do
    let (c, expanded) := stack.head!
    stack := stack.tail!
    if expanded then
      done := done.insert c
      order := order.push c
    else if !done.contains c && !onStack.contains c then
      onStack := onStack.insert c
      stack := (c, true) :: stack
      for r in refsOf c do
        if !done.contains r && !onStack.contains r then stack := (r, false) :: stack
  -- which constants depend on `old`
  let mut dep : NameSet := {}
  for c in order do
    if c == old || (refsOf c).any dep.contains then dep := dep.insert c
  let toCopy := order.filter fun c => dep.contains c && c != old
  let rename (c : Name) : Name := if c == old then new else if dep.contains c then pre ++ c else c
  let tr (e : Expr) : Expr := e.replace fun
    | .const c ls => if c == old || dep.contains c then some (.const (rename c) ls) else none
    | _ => none
  let mut kinds : Std.HashMap String Nat := {}
  let mut typeChanged : Array Name := #[]
  for c in toCopy do
    let some ci := env.find? c | throwError "missing {c}"
    let n := rename c
    let ty := tr ci.type
    if ty != ci.type then typeChanged := typeChanged.push c
    let mut decl : Declaration := .axiomDecl { name := n, levelParams := [], type := ty, isUnsafe := false }
    let mut k := ""
    match ci with
    | .thmInfo t =>
      let tv : TheoremVal := { name := n, levelParams := t.levelParams, type := ty, value := tr t.value }
      decl := .thmDecl tv
      k := "theorem"
    | .defnInfo d =>
      if d.all.length != 1 then throwError "mutual definition {c}: not handled"
      let dv : DefinitionVal := { name := n, levelParams := d.levelParams, type := ty, value := tr d.value, hints := d.hints, safety := d.safety, all := [n] }
      decl := .defnDecl dv
      k := "def"
    | .opaqueInfo o =>
      let ov : OpaqueVal := { name := n, levelParams := o.levelParams, type := ty, value := tr o.value, isUnsafe := o.isUnsafe, all := [n] }
      decl := .opaqueDecl ov
      k := "opaque"
    | _ => throwError "{c} is not a theorem/definition/opaque; cannot reroute"
    kinds := kinds.insert k (kinds.getD k 0 + 1)
    liftCoreM <| addDecl decl
  logInfo m!"closure of roots: {order.size} constants; depending on {old}: {toCopy.size} \
    copied and kernel-checked under {pre}: {toCopy} (kinds: {kinds.toList}); \
    constants whose *type* changed: {typeChanged.size} {typeChanged}"
  for r in roots do
    if !dep.contains r then logWarning m!"{r} does not depend on {old}"
    else logInfo m!"{r} ↦ {rename r}"

-- Only `dirichletRealZeroBound_proof` uses OAI's Corollary 4. `exists_absolute_real_zero_gap` is proved
-- by OAI along a different route that never uses it (results/2026-10-08-lean-main-closure-*.txt), so
-- there is nothing to reroute there; it is listed as a root so `#reroute` reports that explicitly.
#reroute OAI.SiegelZeros.WeightedTorusJets.actual_biquadratic_rectangle_span
  Lemma3.actual_biquadratic_rectangle_span_via_lemma3 Rerouted
  [OAI.SiegelZeros.WeightedTorusJets.dirichletRealZeroBound_proof,
   OAI.SiegelZeros.WeightedTorusJets.exists_absolute_real_zero_gap]

/-! ## Checks -/

-- The rerouted theorem has literally OAI's statement (elaboration checks the types agree).
theorem dirichletRealZeroBound_via_lemma3 :
    type_of% @OAI.SiegelZeros.WeightedTorusJets.dirichletRealZeroBound_proof :=
  Rerouted.OAI.SiegelZeros.WeightedTorusJets.dirichletRealZeroBound_proof

-- Statement restated verbatim from refs/SiegelZeros.lean (the comparator challenge).
theorem challenge_dirichletRealZeroBound_proof :
    ∃ c : ℝ, 0 < c ∧ ∀ (q : ℕ) [NeZero q], 3 ≤ q →
      ∀ χ : DirichletCharacter ℂ q,
        χ.IsPrimitive → χ ≠ 1 → (∀ a : ZMod q, (χ a).im = 0) →
        ∀ β : ℝ,
          (0 < β ∧ β < 1 ∧ DirichletCharacter.LFunction χ (β : ℂ) = 0) →
            c ≤ (1 - β) * Real.log (q : ℝ) :=
  dirichletRealZeroBound_via_lemma3

-- A second check that the rerouted proof is a proof of the right thing: the comparator challenge's
-- other theorem (a curried form of the same statement) follows from it in a few lines.
theorem challenge_exists_absolute_real_zero_gap :
    ∃ c : ℝ, 0 < c ∧
      ∀ (q : ℕ) [NeZero q], 3 ≤ q →
      ∀ χ : DirichletCharacter ℂ q,
        χ.IsPrimitive → χ ≠ 1 → (∀ a : ZMod q, (χ a).im = 0) →
        ∀ β : ℝ, 0 < β → β < 1 → χ.LFunction (β : ℂ) = 0 →
          c ≤ (1 - β) * Real.log (q : ℝ) := by
  obtain ⟨c, hc, h⟩ := challenge_dirichletRealZeroBound_proof
  exact ⟨c, hc, fun q _ hq χ hp h1 hr β h0 hβ hz => h q hq χ hp h1 hr β ⟨h0, hβ, hz⟩⟩

-- Independence: the rerouted proof must not reach OAI's Corollary 4 or its multiplicity route.
#find_deps challenge_dirichletRealZeroBound_proof ["uniform_rectangular_multiplicity", "source_rectangle_span_of_polynomial_zero_test", "actual_biquadratic_rectangle_span"]
#find_deps challenge_exists_absolute_real_zero_gap ["uniform_rectangular_multiplicity", "source_rectangle_span_of_polynomial_zero_test", "actual_biquadratic_rectangle_span"]
-- control: OAI's own proof must match
#find_deps OAI.SiegelZeros.WeightedTorusJets.dirichletRealZeroBound_proof ["uniform_rectangular_multiplicity", "source_rectangle_span_of_polynomial_zero_test", "actual_biquadratic_rectangle_span"]

#print axioms challenge_dirichletRealZeroBound_proof
#print axioms challenge_exists_absolute_real_zero_gap
