import OAI.NumberTheory.SiegelZeros.Main

/-! Query (2026-10-27): the dependency closure of a root constant, with the module each member is defined in.
Same closure as `#find_deps` in ReroutedDeps.lean: transitive over types and values of theorem/def/opaque constants.
Reports: closure size; member count per top-level module prefix (first three name components); every member whose
module is under OAI.NumberTheory.DirichletL (the 7/8 development, Dirichlet and Hecke) or whose name contains
"seven_eighths", "SevenEighths" or "QuasiRiemann"; and whether named constants are members. It proves nothing. -/

open Lean Elab Command in
elab "#closure_modules " n:ident " [" xs:ident,* "]" : command => do
  let env ← getEnv
  let root ← liftCoreM <| realizeGlobalConstNoOverloadWithInfo n
  let probes ← xs.getElems.toList.mapM fun x => liftCoreM <| realizeGlobalConstNoOverloadWithInfo x
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
      let refs := ci.type.getUsedConstants ++ (v.map (·.getUsedConstants) |>.getD #[])
      for r in refs do
        if !seen.contains r then stack := r :: stack
    | none => pure ()
  let modOf (c : Name) : Name := match env.getModuleIdxFor? c with
    | some i => env.header.moduleNames[i.toNat]!
    | none => `«current file»
  let prefix3 (m : Name) : String :=
    let cs := m.components.take 3
    ".".intercalate (cs.map toString)
  let mut counts : Std.HashMap String Nat := {}
  let mut hits : Array String := #[]
  for c in seen.toList do
    let m := modOf c
    counts := counts.insert (prefix3 m) (counts.getD (prefix3 m) 0 + 1)
    let s := c.toString
    if (`OAI.NumberTheory.DirichletL).isPrefixOf m || (s.splitOn "seven_eighths").length > 1
        || (s.splitOn "SevenEighths").length > 1 || (s.splitOn "QuasiRiemann").length > 1 then
      hits := hits.push s!"{s} [{m}]"
  logInfo m!"{root}: {seen.size} constants in closure"
  let sorted := counts.toList.toArray.qsort (fun a b => a.2 > b.2)
  logInfo m!"by module prefix: {sorted.toList}"
  logInfo m!"members from OAI.NumberTheory.DirichletL or named *seven_eighths*/*SevenEighths*/*QuasiRiemann*: {hits.size} {hits.toList}"
  for p in probes do
    logInfo m!"member {p}: {seen.contains p}"

#closure_modules OAI.SiegelZeros.WeightedTorusJets.exists_absolute_real_zero_gap [OAI.SiegelZeros.WeightedTorusJets.dirichletRealZeroBound_proof, OAI.SiegelZeros.WeightedTorusJets.dirichlet_real_zero_bound, OAI.SiegelZeros.WeightedTorusJets.actual_biquadratic_rectangle_span, OAI.SiegelZeros.SiegelZerosAwei.W50.uniform_exclusion_of_local_isolated_bezout, OAI.SiegelZeros.SiegelZerosAwei.W50.uniform_exclusion_of_actual_cutoff]
