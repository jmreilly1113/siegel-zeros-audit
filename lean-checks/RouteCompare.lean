import OAI.NumberTheory.SiegelZeros.Main

/-! Query (2026-10-27): for each root, the dependency closure (same convention as `#find_deps` in ReroutedDeps.lean:
transitive over types and values of theorem/def/opaque constants), the number of members whose first name component
is CategoryTheory or AlgebraicGeometry, and the full names of members whose last name component is one of the given
strings. It proves nothing. Run once in the unmodified clone and once in the rerouted clone. -/

open Lean Elab Command in
elab "#route_compare " n:ident " [" xs:str,* "]" : command => do
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
  let first (c : Name) : String := match c.components with
    | h :: _ => h.toString
    | [] => ""
  let ct := seen.toList.filter (fun c => first c == "CategoryTheory") |>.length
  let ag := seen.toList.filter (fun c => first c == "AlgebraicGeometry") |>.length
  logInfo m!"{root}: {seen.size} constants in closure; CategoryTheory {ct}; AlgebraicGeometry {ag}; matches: {hits}"

#route_compare OAI.SiegelZeros.WeightedTorusJets.exists_absolute_real_zero_gap ["exists_good_mass_for_actual_zeros_normalized", "false_of_eventual_exists_pivot_master", "exists_actual_character_pivot_master", "actualCutoffSpanning_of_localBezout", "actual_complex_cutoff_spanning", "actual_cutoff_spanning_of_localBezout", "actual_rectangularAssertion_of_localBezout", "cutoff_span_of_rectangularAssertion", "uniform_rectangular_multiplicity", "source_rectangle_span_of_polynomial_zero_test", "actual_biquadratic_rectangle_span"]
#route_compare OAI.SiegelZeros.WeightedTorusJets.dirichletRealZeroBound_proof ["exists_good_mass_for_actual_zeros_normalized", "false_of_eventual_exists_pivot_master", "exists_actual_character_pivot_master", "actualCutoffSpanning_of_localBezout", "actual_complex_cutoff_spanning", "actual_cutoff_spanning_of_localBezout", "actual_rectangularAssertion_of_localBezout", "cutoff_span_of_rectangularAssertion", "uniform_rectangular_multiplicity", "source_rectangle_span_of_polynomial_zero_test", "actual_biquadratic_rectangle_span"]
