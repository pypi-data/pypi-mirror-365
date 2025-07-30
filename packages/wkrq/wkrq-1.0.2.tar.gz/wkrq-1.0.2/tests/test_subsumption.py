"""
Tests for subsumption functionality in wKrQ tableau construction.

This module tests the three aspects of subsumption:
1. Propositional subsumption (formula structure)
2. First-order subsumption (term relationships)  
3. Three-valued logic subsumption (sign relationships)
"""

import pytest
from wkrq.formula import (
    PropositionalAtom, 
    PredicateFormula, 
    Variable, 
    Constant,
    conjunction,
    disjunction,
    negation
)
from wkrq.signs import SignedFormula, T, F, M, N
from wkrq.tableau import Branch, TableauNode
from wkrq.api import solve


class TestPropositionalSubsumption:
    """Test propositional subsumption patterns."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.branch = Branch(0)
        self.p = PropositionalAtom("p")
        self.q = PropositionalAtom("q")
        self.r = PropositionalAtom("r")
    
    def test_atom_subsumes_disjunction(self):
        """Test that p subsumes p ∨ q."""
        p_or_q = disjunction(self.p, self.q)
        assert self.branch._propositional_subsumes(self.p, p_or_q)
        assert not self.branch._propositional_subsumes(p_or_q, self.p)
    
    def test_conjunction_subsumes_atom(self):
        """Test that p ∧ q subsumes p."""
        p_and_q = conjunction(self.p, self.q)
        assert self.branch._propositional_subsumes(p_and_q, self.p)
        assert not self.branch._propositional_subsumes(self.p, p_and_q)
    
    def test_nested_disjunction_subsumption(self):
        """Test recursive disjunction handling: p subsumes (p ∨ q) ∨ r."""
        p_or_q = disjunction(self.p, self.q)
        nested = disjunction(p_or_q, self.r)
        assert self.branch._propositional_subsumes(self.p, nested)
    
    def test_nested_conjunction_subsumption(self):
        """Test recursive conjunction handling: (p ∧ q) ∧ r subsumes p."""
        p_and_q = conjunction(self.p, self.q)
        nested = conjunction(p_and_q, self.r)
        assert self.branch._propositional_subsumes(nested, self.p)
    
    def test_no_subsumption_across_connectives(self):
        """Test that p ∧ q does not subsume p ∨ r."""
        p_and_q = conjunction(self.p, self.q)
        p_or_r = disjunction(self.p, self.r)
        assert not self.branch._propositional_subsumes(p_and_q, p_or_r)
        assert not self.branch._propositional_subsumes(p_or_r, p_and_q)
    
    def test_identical_formulas_subsume(self):
        """Test that identical formulas subsume each other."""
        p_or_q = disjunction(self.p, self.q)
        p_or_q_copy = disjunction(self.p, self.q)
        assert self.branch._subsumes(p_or_q, p_or_q_copy)
        assert self.branch._subsumes(p_or_q_copy, p_or_q)


class TestFirstOrderSubsumption:
    """Test first-order subsumption patterns."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.branch = Branch(0)
        self.x = Variable("X")
        self.y = Variable("Y")
        self.a = Constant("a")
        self.b = Constant("b")
    
    def test_universal_subsumes_instance(self):
        """Test that P(X) subsumes P(a)."""
        px = PredicateFormula("P", [self.x])
        pa = PredicateFormula("P", [self.a])
        assert self.branch._first_order_subsumes(px, pa)
        assert not self.branch._first_order_subsumes(pa, px)
    
    def test_multiple_variables_subsumption(self):
        """Test that R(X,Y) subsumes R(a,b)."""
        rxy = PredicateFormula("R", [self.x, self.y])
        rab = PredicateFormula("R", [self.a, self.b])
        assert self.branch._first_order_subsumes(rxy, rab)
    
    def test_partial_variable_subsumption(self):
        """Test that R(X,a) subsumes R(b,a)."""
        rxa = PredicateFormula("R", [self.x, self.a])
        rba = PredicateFormula("R", [self.b, self.a])
        assert self.branch._first_order_subsumes(rxa, rba)
    
    def test_inconsistent_substitution_fails(self):
        """Test that R(X,X) does not subsume R(a,b)."""
        rxx = PredicateFormula("R", [self.x, self.x])
        rab = PredicateFormula("R", [self.a, self.b])
        assert not self.branch._first_order_subsumes(rxx, rab)
    
    def test_consistent_substitution_succeeds(self):
        """Test that R(X,X) subsumes R(a,a)."""
        rxx = PredicateFormula("R", [self.x, self.x])
        raa = PredicateFormula("R", [self.a, self.a])
        assert self.branch._first_order_subsumes(rxx, raa)
    
    def test_different_predicates_no_subsumption(self):
        """Test that P(X) does not subsume Q(a)."""
        px = PredicateFormula("P", [self.x])
        qa = PredicateFormula("Q", [self.a])
        assert not self.branch._first_order_subsumes(px, qa)


class TestThreeValuedSignSubsumption:
    """Test three-valued logic sign subsumption."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.branch = Branch(0)
        self.p = PropositionalAtom("p")
    
    def test_t_subsumes_m(self):
        """Test that T:p subsumes M:p."""
        t_p = SignedFormula(T, self.p)
        m_p = SignedFormula(M, self.p)
        assert self.branch._signed_subsumes(t_p, m_p)
        assert not self.branch._signed_subsumes(m_p, t_p)
    
    def test_f_subsumes_m(self):
        """Test that F:p subsumes M:p."""
        f_p = SignedFormula(F, self.p)
        m_p = SignedFormula(M, self.p)
        assert self.branch._signed_subsumes(f_p, m_p)
        assert not self.branch._signed_subsumes(m_p, f_p)
    
    def test_n_orthogonal_to_others(self):
        """Test that N is orthogonal to T, F, M."""
        n_p = SignedFormula(N, self.p)
        t_p = SignedFormula(T, self.p)
        f_p = SignedFormula(F, self.p)
        m_p = SignedFormula(M, self.p)
        
        # N doesn't subsume others
        assert not self.branch._signed_subsumes(n_p, t_p)
        assert not self.branch._signed_subsumes(n_p, f_p)
        assert not self.branch._signed_subsumes(n_p, m_p)
        
        # Others don't subsume N
        assert not self.branch._signed_subsumes(t_p, n_p)
        assert not self.branch._signed_subsumes(f_p, n_p)
        assert not self.branch._signed_subsumes(m_p, n_p)
    
    def test_no_self_subsumption(self):
        """Test that identical signed formulas don't subsume each other."""
        t_p = SignedFormula(T, self.p)
        t_p_copy = SignedFormula(T, self.p)
        assert not self.branch._signed_subsumes(t_p, t_p_copy)
    
    def test_combined_formula_and_sign_subsumption(self):
        """Test combined formula structure and sign subsumption."""
        q = PropositionalAtom("q")
        p_or_q = disjunction(self.p, q)
        
        # T:p subsumes T:(p ∨ q) - same signs, formula subsumption
        t_p = SignedFormula(T, self.p)
        t_p_or_q = SignedFormula(T, p_or_q)
        assert self.branch._signed_subsumes(t_p, t_p_or_q)
        
        # T:p subsumes M:(p ∨ q) - compatible signs, formula subsumption
        m_p_or_q = SignedFormula(M, p_or_q)
        assert self.branch._signed_subsumes(t_p, m_p_or_q)
        
        # T:p doesn't subsume F:(p ∨ q) - incompatible signs
        f_p_or_q = SignedFormula(F, p_or_q)
        assert not self.branch._signed_subsumes(t_p, f_p_or_q)


class TestBranchSubsumptionIntegration:
    """Test subsumption integration with branch operations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.branch = Branch(0)
        self.node = TableauNode(None, None)
        self.p = PropositionalAtom("p")
        self.q = PropositionalAtom("q")
    
    def test_forward_subsumption_filtering(self):
        """Test that incoming subsumed formulas are rejected."""
        # Add stronger formula first
        t_p = SignedFormula(T, self.p)
        result1 = self.branch.add_formula(t_p, self.node)
        assert not result1  # Should not close branch
        assert t_p in self.branch.formulas
        
        # Try to add weaker formula - should be rejected
        t_p_or_q = SignedFormula(T, disjunction(self.p, self.q))
        result2 = self.branch.add_formula(t_p_or_q, self.node)
        assert not result2  # Should not close branch
        assert t_p_or_q not in self.branch.formulas  # Should be rejected
    
    def test_backward_subsumption_marking(self):
        """Test that existing formulas are marked as subsumed."""
        # Add weaker formula first
        t_p_or_q = SignedFormula(T, disjunction(self.p, self.q))
        self.branch.add_formula(t_p_or_q, self.node)
        assert t_p_or_q in self.branch.formulas
        
        # Add stronger formula - should mark weaker as subsumed
        t_p = SignedFormula(T, self.p)
        self.branch.add_formula(t_p, self.node)
        assert t_p in self.branch.formulas
        assert t_p_or_q in self.branch.subsumed_formulas
    
    def test_atomic_formulas_never_filtered(self):
        """Test that atomic formulas are never filtered by forward subsumption."""
        # Add a signed atom
        t_p = SignedFormula(T, self.p)
        self.branch.add_formula(t_p, self.node)
        
        # Try to add same atom with different sign - should still be added
        f_p = SignedFormula(F, self.p)
        result = self.branch.add_formula(f_p, self.node)
        assert result  # Should close branch due to contradiction
        assert self.branch.is_closed


class TestSubsumptionSoundness:
    """Test that subsumption preserves tableau soundness."""
    
    def test_contradiction_still_detected(self):
        """Test that p ∧ ¬p is still unsatisfiable with subsumption."""
        p = PropositionalAtom("p")
        contradiction = conjunction(p, negation(p))
        result = solve(contradiction, T)
        assert not result.satisfiable
        assert len(result.models) == 0
    
    def test_tautology_still_detected(self):
        """Test that p ∨ ¬p is still a tautology with subsumption."""
        p = PropositionalAtom("p")
        tautology = disjunction(p, negation(p))
        result = solve(tautology, F)  # Test if ¬(p ∨ ¬p) is unsatisfiable
        assert not result.satisfiable
    
    def test_valid_inference_preserved(self):
        """Test that valid inferences still work with subsumption."""
        p = PropositionalAtom("p")
        q = PropositionalAtom("q")
        
        # Test modus ponens: p, p → q ⊢ q
        from wkrq.api import entails
        premises = [p, p.implies(q)]
        conclusion = q
        assert entails(premises, conclusion)
    
    def test_invalid_inference_rejected(self):
        """Test that invalid inferences are still rejected with subsumption."""
        p = PropositionalAtom("p")
        q = PropositionalAtom("q")
        
        # Test invalid: p ⊢ q
        from wkrq.api import entails
        premises = [p]
        conclusion = q
        assert not entails(premises, conclusion)


class TestSubsumptionPerformance:
    """Test subsumption performance characteristics."""
    
    def test_redundant_formulas_optimized(self):
        """Test that redundant formulas are optimized away."""
        p = PropositionalAtom("p")
        q = PropositionalAtom("q")
        r = PropositionalAtom("r")
        
        # Create formula with redundancy: p ∨ (p ∨ q) ∨ (p ∨ q ∨ r)
        # p should subsume the more complex disjunctions
        p_or_q = disjunction(p, q)
        p_or_q_or_r = disjunction(p_or_q, r)
        redundant_formula = disjunction(disjunction(p, p_or_q), p_or_q_or_r)
        
        result = solve(redundant_formula, T)
        assert result.satisfiable
        # Should solve efficiently without expanding redundant subformulas
        assert result.total_nodes < 20  # Reasonable upper bound
    
    def test_first_order_redundancy_optimized(self):
        """Test that first-order redundancy is optimized."""
        x = Variable("X")
        a = Constant("a")
        px = PredicateFormula("P", [x])
        pa = PredicateFormula("P", [a])
        
        # P(X) ∧ P(a) - P(a) should be subsumed by P(X)
        redundant = conjunction(px, pa)
        result = solve(redundant, T)
        assert result.satisfiable
        # Should recognize that P(a) is redundant given P(X)
        assert result.total_nodes < 10


# Integration test to ensure all subsumption aspects work together
class TestSubsumptionIntegration:
    """Integration tests for all subsumption aspects."""
    
    def test_all_subsumption_types_together(self):
        """Test propositional, first-order, and sign subsumption together."""
        # Create scenarios that combine different subsumption types
        x = Variable("X")
        a = Constant("a")
        px = PredicateFormula("P", [x])
        pa = PredicateFormula("P", [a])
        q = PropositionalAtom("q")
        
        branch = Branch(0)
        node = TableauNode(None, None)
        
        # Test 1: First-order + sign subsumption
        t_px = SignedFormula(T, px)
        m_pa = SignedFormula(M, pa)
        assert branch._signed_subsumes(t_px, m_pa), "T:P(X) should subsume M:P(a)"
        
        # Test 2: Propositional + sign subsumption  
        t_pa = SignedFormula(T, pa)
        pa_or_q = disjunction(pa, q)
        m_pa_or_q = SignedFormula(M, pa_or_q)
        assert branch._signed_subsumes(t_pa, m_pa_or_q), "T:P(a) should subsume M:(P(a) ∨ q)"
        
        # Test 3: Branch integration with combined subsumption
        branch.add_formula(t_px, node)
        
        # Try to add atomic formula - should be added despite subsumption (preserves completeness)
        result = branch.add_formula(m_pa, node)
        assert not result, "Should not close branch"
        assert m_pa in branch.formulas, "Atomic formulas are always added for completeness"
        
        # But it should be marked as subsumed afterward
        assert m_pa in branch.subsumed_formulas, "M:P(a) should be marked as subsumed"
        
        # Verify direct subsumption relationships
        assert branch._signed_subsumes(t_px, m_pa)
        assert branch._signed_subsumes(t_pa, m_pa_or_q)