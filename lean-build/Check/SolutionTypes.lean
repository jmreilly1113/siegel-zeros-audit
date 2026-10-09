import OAI.NumberTheory.SiegelZeros.Main

open Lean Elab Command in
#eval show CommandElabM Unit from do
  let env ← getEnv
  for n in [`OAI.SiegelZeros.WeightedTorusJets.exists_absolute_real_zero_gap,
            `OAI.SiegelZeros.WeightedTorusJets.dirichletRealZeroBound_proof] do
    let some ci := env.find? n | throwError "missing {n}"
    IO.println s!"TYPE {n} hash={ci.type.hash}"
    IO.println s!"EXPR {n} {ci.type}"
