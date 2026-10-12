#!/usr/bin/env bash
# Generates the four Lean-level query files from _template.lean.in.
cd "$(dirname "$0")"
g() { sed -e "s/@MODULE@/$2/g" -e "s/@THM@/$3/g" -e "s/@TARGET@/$4/g" _template.lean.in > $1.lean; }
g HarmonicGrowthChallenge ComparatorChallenges.HarmonicGrowth OAI.HarmonicCounterexample.main OAI.HarmonicCounterexample.mainStatement
g HarmonicGrowthSolution OAI.Geometry.HarmonicGrowth.Main OAI.HarmonicCounterexample.main OAI.HarmonicCounterexample.mainStatement
g NavierStokesChallenge ComparatorChallenges.NavierStokesVelocity OAI.VelocityDetection.main_result OAI.VelocityDetection.TapeCodes.half
g NavierStokesSolution OAI.MathematicalPhysics.NavierStokes.VelocityDetection.Main OAI.VelocityDetection.main_result OAI.VelocityDetection.TapeCodes.half
