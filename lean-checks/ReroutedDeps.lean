import OAI.NumberTheory.SiegelZeros.Main

/-! Dependency scan for plan step 3d. Same scan as `#find_deps` in Lemma3Bridged.lean: transitive closure over
types and values of theorem/def/opaque constants, reporting closure members whose last name component is one of
the given strings. Compiled once in the rerouted clone and once, as the control, in the unmodified clone. -/

open Lean Elab Command in
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

#find_deps OAI.SiegelZeros.WeightedTorusJets.dirichletRealZeroBound_proof ["uniform_rectangular_multiplicity", "source_rectangle_span_of_polynomial_zero_test", "actual_biquadratic_rectangle_span", "actual_biquadratic_rectangle_span_via_lemma3", "interpolation"]
#find_deps OAI.SiegelZeros.WeightedTorusJets.exists_absolute_real_zero_gap ["uniform_rectangular_multiplicity", "source_rectangle_span_of_polynomial_zero_test", "actual_biquadratic_rectangle_span", "actual_biquadratic_rectangle_span_via_lemma3", "interpolation"]
#print axioms OAI.SiegelZeros.WeightedTorusJets.dirichletRealZeroBound_proof
#print axioms OAI.SiegelZeros.WeightedTorusJets.exists_absolute_real_zero_gap
