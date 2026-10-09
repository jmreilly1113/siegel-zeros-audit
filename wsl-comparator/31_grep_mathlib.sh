#!/usr/bin/env bash
M=/home/checker/math/lean/.lake/packages/mathlib/Mathlib
grep -rn "theorem\|lemma" $M/NumberTheory/DirichletCharacter/Basic.lean | grep -i "primitive\|conductor" | cut -c1-220 | head -30
echo ===
grep -rn "LFunction_eq_LSeries\|theorem LFunction_apply_one_ne_zero\|LFunction_ne_zero_of_one_le_re" $M/NumberTheory | cut -c1-220 | head
echo ===
grep -rln "quadraticChar" $M | head; grep -rn "def χ₄\|χ₄ :" $M | head -3
