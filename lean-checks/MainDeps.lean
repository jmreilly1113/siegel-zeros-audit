import OAI.NumberTheory.SiegelZeros.Main

/-! Which constants does OAI's main theorem depend on? Lists closure members (types and values of
theorem/def/opaque, types of everything else) whose full name contains one of the given substrings. -/

open Lean Elab Command in
elab "#deps_matching " n:ident " [" xs:str,* "]" : command => do
  let env ← getEnv
  let pats := xs.getElems.toList.map (·.getString)
  let root ← liftCoreM <| realizeGlobalConstNoOverloadWithInfo n
  let mut seen : NameSet := {}
  let mut stack : List Name := [root]
  while !stack.isEmpty do
    let c := stack.head!
    stack := stack.tail!
    if seen.contains c then continue
    seen := seen.insert c
    match env.find? c with
    | some ci =>
      let v : Option Expr := match ci with
        | .thmInfo t => some t.value
        | .defnInfo d => some d.value
        | .opaqueInfo o => some o.value
        | _ => none
      for r in ci.type.getUsedConstants ++ (v.map (·.getUsedConstants) |>.getD #[]) do
        if !seen.contains r then stack := r :: stack
    | none => logWarning m!"not found: {c}"
  for p in pats do
    let hits := seen.toList.filter fun c => (c.toString.splitOn p).length > 1
    let hits := hits.toArray.qsort (·.toString < ·.toString)
    logInfo m!"{root}: {seen.size} constants; containing \"{p}\": {hits.size}\n{hits}"

#deps_matching OAI.SiegelZeros.WeightedTorusJets.exists_absolute_real_zero_gap
  ["actual_biquadratic", "rectangle", "multiplicity", "interpolation", "InvariantJet"]
-- control: Corollary 4 itself
#deps_matching OAI.SiegelZeros.WeightedTorusJets.actual_biquadratic_rectangle_span ["multiplicity"]
