import StatementChecks.HeckeNontrivial

/-! The norm identity behind the lattice series: `Algebra.norm ℤ (x + y ω) = x² - x y + y²` in `O = 𝓞 K`,
computed as the determinant of multiplication by `x + y ω` in the integral power basis `{1, ω}`. -/

open OAI.SevenEighths OAI.SevenEighths.HeckeFamily

namespace StatementChecks.HeckeNorm

local notation "hζ" => IsCyclotomicExtension.zeta_spec 3 ℚ K

noncomputable def pb := (hζ).integralPowerBasis

lemma pb_dim : pb.dim = 2 := by
  simp [pb, IsPrimitiveRoot.integralPowerBasis_dim, Nat.totient_prime Nat.prime_three]

lemma pb_gen : pb.gen = omega := by simp [pb, omega, IsPrimitiveRoot.integralPowerBasis_gen]

/-- The basis `{1, ω}` indexed by `Fin 2`. -/
noncomputable def b : Module.Basis (Fin 2) ℤ O := pb.basis.reindex (finCongr pb_dim)

lemma b0 : b 0 = 1 := by
  simp [b, PowerBasis.coe_basis, Module.Basis.reindex_apply]

lemma b1 : b 1 = omega := by
  simp [b, PowerBasis.coe_basis, Module.Basis.reindex_apply, pb_gen]

lemma repr_comb (c₀ c₁ : ℤ) : b.repr ((c₀ : O) + (c₁ : O) * omega) = Finsupp.single 0 c₀ + Finsupp.single 1 c₁ := by
  have h : (c₀ : O) + (c₁ : O) * omega = c₀ • b 0 + c₁ • b 1 := by
    rw [b0, b1, zsmul_eq_mul, zsmul_eq_mul, mul_one]
  rw [h, map_add, map_zsmul, map_zsmul, b.repr_self, b.repr_self, Finsupp.smul_single_one,
    Finsupp.smul_single_one]

/-- `N(x + y ω) = x² - x y + y²`. -/
theorem norm_coordinateElement (x y : ℤ) :
    Algebra.norm ℤ (coordinateElement x y) = x ^ 2 - x * y + y ^ 2 := by
  rw [Algebra.norm_eq_matrix_det b, Matrix.det_fin_two]
  simp only [Algebra.leftMulMatrix_eq_repr_mul, b0, b1, mul_one, coordinateElement]
  have h1 : ((x : O) + (y : O) * omega) * omega = ((-y : ℤ) : O) + ((x - y : ℤ) : O) * omega := by
    have := StatementChecks.HeckeNontrivial.omega_sq
    push_cast
    linear_combination y * this
  rw [h1, repr_comb, repr_comb]
  simp [Finsupp.single_apply]
  ring

/-- The same for the ideal norm used by the paper (`N𝔞 = |O/𝔞|`, paper.tex l.51): the principal ideal
`(x + y ω)` has absolute norm `x² - x y + y²`. -/
theorem absNorm_span_coordinateElement (x y : ℤ) :
    Ideal.absNorm (Ideal.span {coordinateElement x y}) = (x ^ 2 - x * y + y ^ 2).natAbs := by
  rw [Ideal.absNorm_span_singleton, norm_coordinateElement]

end StatementChecks.HeckeNorm

#print axioms StatementChecks.HeckeNorm.norm_coordinateElement
#print axioms StatementChecks.HeckeNorm.absNorm_span_coordinateElement
