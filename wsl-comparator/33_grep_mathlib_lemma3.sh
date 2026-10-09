#!/bin/bash
# Inspection only: which Lemma 3 ingredients Mathlib (d13f23b723) already has.
cd /home/checker/math/lean/.lake/packages/mathlib/Mathlib || exit 1
git -C .. rev-parse HEAD
grep -rn "^theorem eq_pos_convex_span_of_mem_convexHull\|^theorem convexHull_eq_union" Analysis/Convex/
grep -rn "^theorem norm_eq_iInf_iff_real_inner_le_zero\|^theorem exists_norm_eq_iInf_of_complete_convex" Analysis/
grep -rn "^def interpolate\|^theorem eval_interpolate_at_node" LinearAlgebra/
grep -rn "^def IsExposed\|^theorem IsExposed.isExtreme\|^theorem IsExposed.isClosed" Analysis/Convex/
grep -rln "MvPolynomial.funext\|theorem MvPolynomial.eq_zero_of_eval_zero" . | head -3
