-- Corpus check, Lean-level query (generated from _template.lean.in by scripts/extended_plan.py; do not edit the generated files).
-- Environment: OAI.Combinatorics.Chromatic.Main. Run with `lake env lean <this file>` inside the checker sandbox (wsl-comparator/75_headline_batch.sh).
import OAI.Combinatorics.Chromatic.Main
import Lean
open Lean Elab Command

/-- Constants reachable from `roots`. Types are always followed. Values are followed for definitions and opaques
(what a statement means), and also for theorems when `proofs` is true. Inductives add their constructors,
constructors their inductive, recursors their block. -/
def auditReach (env : Environment) (roots : Array Name) (proofs : Bool) : NameSet := Id.run do
  let mut seen : NameSet := {}
  let mut stack := roots
  while !stack.isEmpty do
    let n := stack.back!
    stack := stack.pop
    if seen.contains n then continue
    seen := seen.insert n
    match env.find? n with
    | none => pure ()
    | some ci =>
      let mut cs := ci.type.getUsedConstants
      match ci with
      | .defnInfo d => cs := cs ++ d.value.getUsedConstants
      | .opaqueInfo o => cs := cs ++ o.value.getUsedConstants
      | .thmInfo t => if proofs then cs := cs ++ t.value.getUsedConstants
      | .inductInfo i => cs := cs ++ i.ctors.toArray
      | .ctorInfo c => cs := cs.push c.induct
      | .recInfo r => cs := cs ++ r.all.toArray
      | _ => pure ()
      for c in cs do
        if !seen.contains c then stack := stack.push c
  return seen

/-- The value of a definition, theorem or opaque. (`ConstantInfo.value?` returned none for an imported theorem here.) -/
def auditValue : ConstantInfo → Array Name
  | .defnInfo d => d.value.getUsedConstants
  | .thmInfo t => t.value.getUsedConstants
  | .opaqueInfo o => o.value.getUsedConstants
  | _ => #[]

elab "#audit_query " thm:ident target:ident : command => do
  let env ← getEnv
  let t := thm.getId
  let g := target.getId
  let some ci := env.find? t | throwError "AUDIT constant not found: {t}"
  let axs ← collectAxioms t
  let srt (a : Array Name) := a.qsort (fun x y => x.toString < y.toString)
  let stmt := auditReach env ci.type.getUsedConstants false
  let full := auditReach env (ci.type.getUsedConstants ++ auditValue ci) true
  let axIn (s : NameSet) := srt (s.toArray.filter fun n => (env.find? n).any (·.isAxiom))
  let last := g.components.getLast!
  let sameLast (s : NameSet) := srt (s.toArray.filter fun n => n.components.getLast? == some last)
  logInfo m!"AUDIT module OAI.Combinatorics.Chromatic.Main\nAUDIT theorem {t} kind {if ci.isThm then "theorem" else "other"}\nAUDIT axioms ({axs.size}): {srt axs}\nAUDIT target {g} in environment: {env.contains g}{if (env.find? g).any (·.isAxiom) then " (declared as axiom)" else ""}\nAUDIT statement closure: {stmt.size} constants; contains target: {stmt.contains g}; axioms in it: {axIn stmt}; names ending in {last}: {sameLast stmt}\nAUDIT statement+proof closure: {full.size} constants; contains target: {full.contains g}; axioms in it: {axIn full}; names ending in {last}: {sameLast full}"

#audit_query OAI.elementaryPositivityWitness OAI.elementaryPositivityWitness
