# ACrQ Implementation Guide: Extending wKrQ with Analytic Containment

**Version**: 1.0.7  
**Date**: July 2025  
**Based on**: Ferguson, T.M. (2021). "Tableaux and Restricted Quantification for Systems Related to Weak Kleene Logic"

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Theoretical Foundation](#theoretical-foundation)
3. [Architecture Overview](#architecture-overview)
4. [Implementation Strategy](#implementation-strategy)
5. [Detailed Component Design](#detailed-component-design)
6. [Tableau Rules for ACrQ](#tableau-rules-for-acrq)
7. [Migration Path](#migration-path)
8. [Testing Strategy](#testing-strategy)
9. [Future Considerations](#future-considerations)

## Executive Summary

ACrQ (Analytic Containment with restricted Quantification) extends our existing wKrQ implementation with **bilateral predicates** to support relevance logic reasoning. The key innovation is that each predicate R gets a corresponding R* that tracks falsity conditions, enabling fine-grained reasoning about relevance and containment relationships.

### Key Features of ACrQ

1. **Bilateral Predicates**: Every predicate R has a dual R* for tracking falsity
2. **Generalized Truth Values**: Richer truth value space through R/R* combinations
3. **Relevance Logic**: Captures Angell's analytic containment intuitions
4. **Ferguson's Translation**: Systematic translation from wKrQ to ACrQ (Definition 17)
5. **Extended Tableau System**: New rules for bilateral predicate reasoning

### Benefits Over Pure wKrQ

- **Relevance Reasoning**: Can express "A is relevant to B" relationships
- **Fine-grained Falsity**: Distinguishes between "not true" and "actively false"
- **Philosophical Applications**: Better models intentional contexts and belief systems
- **Backward Compatibility**: ACrQ includes wKrQ as a special case

## Theoretical Foundation

### Bilateral Interpretation (Ferguson's Framework)

In ACrQ, each predicate symbol R gets two interpretations:
- **R**: The positive extension (when R holds)
- **R***: The negative extension (when R explicitly fails)

This creates four possible states for any predicate instance R(a):
1. **R(a)=t, R*(a)=f**: Clearly true
2. **R(a)=f, R*(a)=t**: Clearly false
3. **R(a)=f, R*(a)=f**: Neither true nor false (gap)
4. **R(a)=t, R*(a)=t**: Both true and false (glut) - *inconsistent*

### Translation from wKrQ to ACrQ (Definition 17)

Ferguson provides a systematic translation τ:

```
τ(p) = p                           (atoms unchanged)
τ(¬φ) = ¬τ(φ)                     (negation preserved)
τ(φ ∧ ψ) = τ(φ) ∧ τ(ψ)            (conjunction preserved)
τ(φ ∨ ψ) = τ(φ) ∨ τ(ψ)            (disjunction preserved)
τ(R(t₁,...,tₙ)) = R(t₁,...,tₙ)    (positive predicates unchanged)
τ(¬R(t₁,...,tₙ)) = R*(t₁,...,tₙ)  (negated predicates become R*)
```

### Semantic Conditions

ACrQ models must satisfy:
- **Consistency**: For no R and tuple ā, both R(ā)=t and R*(ā)=t
- **Exhaustiveness** (optional): For each R and ā, either R(ā)=t or R*(ā)=t or both=f

### Tableau Closure (Lemma 5)

A branch closes in ACrQ when:
1. **Standard contradiction**: t:φ and f:φ appear
2. **Bilateral contradiction**: t:R(ā) and t:R*(ā) appear
3. **Other sign conflicts**: As in wKrQ

## Architecture Overview

### System Layers

```
ACrQ System Architecture
├── Core Layer (Shared with wKrQ)
│   ├── Basic Formula Types
│   ├── Three-valued Semantics
│   ├── Sign System (T, F, M, N)
│   └── Core Tableau Engine
├── ACrQ Extension Layer
│   ├── Bilateral Predicate Types
│   ├── Extended Truth Values
│   ├── Translation Framework
│   └── ACrQ-specific Rules
├── System Selection Layer
│   ├── Logic System Enum
│   ├── Dynamic Rule Selection
│   └── System-specific Behavior
└── API Layer
    ├── Unified Interface
    ├── System Configuration
    └── Result Interpretation
```

### Component Relationships

```python
# Core components extended for ACrQ
Formula (ABC)
├── PropositionalAtom
├── CompoundFormula
├── PredicateFormula
├── BilateralPredicateFormula (NEW)
├── RestrictedExistentialFormula
└── RestrictedUniversalFormula

# Truth value system
TruthValue
├── Standard: TRUE, FALSE, UNDEFINED
└── Bilateral: BilateralTruthValue (NEW)

# Tableau system
Tableau
├── StandardTableau (wKrQ)
└── ACrQTableau (NEW)
    ├── Bilateral rule handling
    ├── Extended closure detection
    └── ACrQ model extraction
```

## Implementation Strategy

### Phase 1: Foundation (Core Data Structures)

#### 1.1 Bilateral Predicate Formula

```python
@dataclass
class BilateralPredicateFormula(Formula):
    """A bilateral predicate R/R* for ACrQ."""
    
    positive_name: str      # R
    negative_name: str      # R*
    terms: List[Term]
    is_negative: bool = False  # True if this represents R*
    
    def __post_init__(self):
        if not self.negative_name:
            self.negative_name = f"{self.positive_name}*"
    
    def __str__(self) -> str:
        name = self.negative_name if self.is_negative else self.positive_name
        if not self.terms:
            return name
        term_str = ", ".join(str(t) for t in self.terms)
        return f"{name}({term_str})"
    
    def get_dual(self) -> "BilateralPredicateFormula":
        """Return the dual predicate (R ↔ R*)."""
        return BilateralPredicateFormula(
            positive_name=self.positive_name,
            negative_name=self.negative_name,
            terms=self.terms,
            is_negative=not self.is_negative
        )
    
    def to_standard_predicates(self) -> Tuple[PredicateFormula, PredicateFormula]:
        """Convert to pair of standard predicates (R, R*)."""
        pos = PredicateFormula(self.positive_name, self.terms)
        neg = PredicateFormula(self.negative_name, self.terms)
        return (pos, neg)
```

#### 1.2 Bilateral Truth Value

```python
@dataclass
class BilateralTruthValue:
    """Truth value for bilateral predicates in ACrQ."""
    
    positive: TruthValue  # Value for R
    negative: TruthValue  # Value for R*
    
    def __post_init__(self):
        # Enforce consistency constraint
        if self.positive == TRUE and self.negative == TRUE:
            raise ValueError("Bilateral inconsistency: R and R* cannot both be true")
    
    def is_consistent(self) -> bool:
        """Check if the bilateral value is consistent."""
        return not (self.positive == TRUE and self.negative == TRUE)
    
    def is_gap(self) -> bool:
        """Check if neither R nor R* is true (truth value gap)."""
        return self.positive == FALSE and self.negative == FALSE
    
    def is_determinate(self) -> bool:
        """Check if exactly one of R or R* is true."""
        return (self.positive == TRUE and self.negative == FALSE) or \
               (self.positive == FALSE and self.negative == TRUE)
```

### Phase 2: Translation Framework

#### 2.1 Formula Translator

```python
class ACrQTranslator:
    """Translates between wKrQ and ACrQ formulas."""
    
    def translate_to_acrq(self, formula: Formula) -> Formula:
        """Translate wKrQ formula to ACrQ using Ferguson's Definition 17."""
        
        if isinstance(formula, PropositionalAtom):
            # Atoms unchanged
            return formula
            
        elif isinstance(formula, CompoundFormula):
            if formula.connective == "~":
                # Handle negation of predicates specially
                sub = formula.subformulas[0]
                if isinstance(sub, PredicateFormula):
                    # ¬R(x) becomes R*(x)
                    return BilateralPredicateFormula(
                        positive_name=sub.predicate_name,
                        negative_name=f"{sub.predicate_name}*",
                        terms=sub.terms,
                        is_negative=True
                    )
                else:
                    # Recursively translate subformula
                    return Negation(self.translate_to_acrq(sub))
                    
            else:
                # Other connectives: translate subformulas
                new_subs = [self.translate_to_acrq(sub) for sub in formula.subformulas]
                return CompoundFormula(formula.connective, new_subs)
                
        elif isinstance(formula, PredicateFormula):
            # Positive predicates become bilateral with is_negative=False
            return BilateralPredicateFormula(
                positive_name=formula.predicate_name,
                negative_name=f"{formula.predicate_name}*",
                terms=formula.terms,
                is_negative=False
            )
            
        elif isinstance(formula, RestrictedQuantifierFormula):
            # Translate restriction and matrix
            new_restriction = self.translate_to_acrq(formula.restriction)
            new_matrix = self.translate_to_acrq(formula.matrix)
            return formula.__class__(formula.var, new_restriction, new_matrix)
            
        else:
            return formula
    
    def translate_from_acrq(self, formula: Formula) -> Formula:
        """Translate ACrQ formula back to wKrQ (when possible)."""
        
        if isinstance(formula, BilateralPredicateFormula):
            if formula.is_negative:
                # R*(x) becomes ¬R(x)
                pred = PredicateFormula(formula.positive_name, formula.terms)
                return Negation(pred)
            else:
                # R(x) becomes R(x)
                return PredicateFormula(formula.positive_name, formula.terms)
                
        elif isinstance(formula, CompoundFormula):
            # Recursively translate subformulas
            new_subs = [self.translate_from_acrq(sub) for sub in formula.subformulas]
            return CompoundFormula(formula.connective, new_subs)
            
        else:
            return formula
```

### Phase 3: Extended Tableau Engine

#### 3.1 ACrQ-Specific Tableau

```python
class ACrQTableau(Tableau):
    """Extended tableau for ACrQ with bilateral predicate support."""
    
    def __init__(self, initial_formulas: List[SignedFormula]):
        super().__init__(initial_formulas)
        self.logic_system = "ACrQ"
        self.bilateral_pairs: Dict[str, str] = {}  # Maps R to R*
        
        # Identify bilateral predicates in initial formulas
        self._identify_bilateral_predicates(initial_formulas)
    
    def _identify_bilateral_predicates(self, formulas: List[SignedFormula]):
        """Identify and register bilateral predicate pairs."""
        for sf in formulas:
            self._extract_bilateral_pairs(sf.formula)
    
    def _extract_bilateral_pairs(self, formula: Formula):
        """Extract bilateral predicate pairs from a formula."""
        if isinstance(formula, BilateralPredicateFormula):
            self.bilateral_pairs[formula.positive_name] = formula.negative_name
            self.bilateral_pairs[formula.negative_name] = formula.positive_name
        elif isinstance(formula, CompoundFormula):
            for sub in formula.subformulas:
                self._extract_bilateral_pairs(sub)
        elif hasattr(formula, 'restriction') and hasattr(formula, 'matrix'):
            self._extract_bilateral_pairs(formula.restriction)
            self._extract_bilateral_pairs(formula.matrix)
    
    def _check_bilateral_contradiction(self, branch: Branch, new_formula: SignedFormula) -> bool:
        """Check for bilateral contradictions (Lemma 5)."""
        
        # Standard contradiction check
        if super()._check_contradiction(new_formula):
            return True
        
        # Check for bilateral contradiction: t:R(a) and t:R*(a)
        if new_formula.sign == T and isinstance(new_formula.formula, PredicateFormula):
            pred_name = new_formula.formula.predicate_name
            
            # Check if this is part of a bilateral pair
            if pred_name in self.bilateral_pairs:
                dual_name = self.bilateral_pairs[pred_name]
                
                # Look for t:R*(a) if we have t:R(a) (or vice versa)
                for node in branch.nodes:
                    if (node.formula.sign == T and 
                        isinstance(node.formula.formula, PredicateFormula) and
                        node.formula.formula.predicate_name == dual_name and
                        node.formula.formula.terms == new_formula.formula.terms):
                        
                        branch.closure_reason = f"Bilateral contradiction: {pred_name} and {dual_name}"
                        return True
        
        return False
```

#### 3.2 ACrQ-Specific Rules

```python
def _get_acrq_rules(self, signed_formula: SignedFormula, branch: Branch) -> Optional[RuleInfo]:
    """Get ACrQ-specific tableau rules."""
    
    formula = signed_formula.formula
    sign = signed_formula.sign
    
    # Handle bilateral predicates
    if isinstance(formula, BilateralPredicateFormula):
        pos_pred, neg_pred = formula.to_standard_predicates()
        
        if sign == T:
            if formula.is_negative:
                # T: R*(x) means R(x) is false and R*(x) is true
                conclusions = [
                    [SignedFormula(F, pos_pred), SignedFormula(T, neg_pred)]
                ]
                return RuleInfo("T-BilateralNeg", RuleType.ALPHA, 1, 2, conclusions)
            else:
                # T: R(x) means R(x) is true and R*(x) is false
                conclusions = [
                    [SignedFormula(T, pos_pred), SignedFormula(F, neg_pred)]
                ]
                return RuleInfo("T-BilateralPos", RuleType.ALPHA, 1, 2, conclusions)
                
        elif sign == F:
            if formula.is_negative:
                # F: R*(x) branches: either R(x) is true or both undefined
                conclusions = [
                    [SignedFormula(T, pos_pred)],
                    [SignedFormula(N, pos_pred), SignedFormula(N, neg_pred)]
                ]
                return RuleInfo("F-BilateralNeg", RuleType.BETA, 10, 3, conclusions)
            else:
                # F: R(x) branches: either R*(x) is true or both undefined
                conclusions = [
                    [SignedFormula(T, neg_pred)],
                    [SignedFormula(N, pos_pred), SignedFormula(N, neg_pred)]
                ]
                return RuleInfo("F-BilateralPos", RuleType.BETA, 10, 3, conclusions)
                
        elif sign == M:
            # M: R(x) means R(x) can be true or false (but not undefined)
            # This requires considering R* appropriately
            if formula.is_negative:
                conclusions = [
                    [SignedFormula(M, neg_pred)],
                    [SignedFormula(F, pos_pred), SignedFormula(F, neg_pred)]
                ]
            else:
                conclusions = [
                    [SignedFormula(M, pos_pred)],
                    [SignedFormula(F, pos_pred), SignedFormula(F, neg_pred)]
                ]
            return RuleInfo(f"M-Bilateral{'Neg' if formula.is_negative else 'Pos'}", 
                          RuleType.BETA, 20, 3, conclusions)
                          
        elif sign == N:
            # N: R(x) means R(x) is undefined
            # In bilateral interpretation, this typically means gap (both false)
            conclusions = [
                [SignedFormula(F, pos_pred), SignedFormula(F, neg_pred)]
            ]
            return RuleInfo(f"N-Bilateral{'Neg' if formula.is_negative else 'Pos'}", 
                          RuleType.ALPHA, 5, 2, conclusions)
    
    # Handle negation of bilateral predicates
    elif isinstance(formula, CompoundFormula) and formula.connective == "~":
        sub = formula.subformulas[0]
        if isinstance(sub, BilateralPredicateFormula):
            # Negation swaps the bilateral predicate
            dual = sub.get_dual()
            conclusions = [[SignedFormula(sign, dual)]]
            return RuleInfo("Bilateral-Negation", RuleType.ALPHA, 0, 1, conclusions)
    
    return None
```

### Phase 4: Model Extraction

#### 4.1 ACrQ Model Structure

```python
@dataclass
class ACrQModel(Model):
    """Model for ACrQ with bilateral predicate support."""
    
    bilateral_valuations: Dict[str, BilateralTruthValue]
    
    def __init__(self, branch: Branch, bilateral_pairs: Dict[str, str]):
        """Extract model from an open branch."""
        
        # Group predicates by their base name
        predicate_groups: Dict[str, Dict[str, TruthValue]] = defaultdict(dict)
        
        for node in branch.nodes:
            if isinstance(node.formula.formula, PredicateFormula):
                pred = node.formula.formula
                key = str(pred)
                
                # Determine truth value from sign
                if node.formula.sign == T:
                    value = TRUE
                elif node.formula.sign == F:
                    value = FALSE
                elif node.formula.sign == N:
                    value = UNDEFINED
                else:  # M sign
                    value = TRUE  # Could also be FALSE
                
                predicate_groups[pred.predicate_name][key] = value
        
        # Build bilateral valuations
        self.bilateral_valuations = {}
        processed = set()
        
        for pred_name, values in predicate_groups.items():
            if pred_name in processed:
                continue
                
            # Find the bilateral pair
            if pred_name in bilateral_pairs:
                dual_name = bilateral_pairs[pred_name]
                processed.add(pred_name)
                processed.add(dual_name)
                
                # Get values for both predicates
                for pred_instance in values:
                    # Extract the terms from the predicate instance
                    base_key = pred_instance.replace(pred_name, "").strip("()")
                    
                    pos_val = values.get(f"{pred_name}({base_key})", UNDEFINED)
                    neg_val = predicate_groups.get(dual_name, {}).get(f"{dual_name}({base_key})", UNDEFINED)
                    
                    # Create bilateral truth value
                    try:
                        bilateral_val = BilateralTruthValue(pos_val, neg_val)
                        self.bilateral_valuations[f"{pred_name}({base_key})"] = bilateral_val
                    except ValueError:
                        # Inconsistent - this shouldn't happen in an open branch
                        pass
        
        # Create standard valuations for compatibility
        standard_vals = {}
        for key, bilateral_val in self.bilateral_valuations.items():
            standard_vals[key] = bilateral_val.positive
            # Also add R* valuations
            base = key.split("(")[0]
            if base in bilateral_pairs:
                dual_key = key.replace(base, bilateral_pairs[base])
                standard_vals[dual_key] = bilateral_val.negative
        
        super().__init__(standard_vals, {})
```

### Phase 5: API Integration

#### 5.1 System Selection

```python
from enum import Enum

class LogicalSystem(Enum):
    """Available logical systems."""
    WKRQ = "wKrQ"
    ACRQ = "ACrQ"
    SRQ = "SrQ"  # Future extension

class SystemSelector:
    """Selects appropriate tableau system based on formula content."""
    
    @staticmethod
    def detect_system(formulas: List[Formula]) -> LogicalSystem:
        """Auto-detect the required logical system."""
        
        for formula in formulas:
            if SystemSelector._contains_bilateral_predicate(formula):
                return LogicalSystem.ACRQ
        
        return LogicalSystem.WKRQ
    
    @staticmethod
    def _contains_bilateral_predicate(formula: Formula) -> bool:
        """Check if formula contains bilateral predicates."""
        if isinstance(formula, BilateralPredicateFormula):
            return True
        elif isinstance(formula, CompoundFormula):
            return any(SystemSelector._contains_bilateral_predicate(sub) 
                      for sub in formula.subformulas)
        elif hasattr(formula, 'restriction') and hasattr(formula, 'matrix'):
            return (SystemSelector._contains_bilateral_predicate(formula.restriction) or
                    SystemSelector._contains_bilateral_predicate(formula.matrix))
        return False
```

#### 5.2 Extended API

```python
def solve_acrq(formula: Formula, sign: Sign = T, 
               system: Optional[LogicalSystem] = None) -> TableauResult:
    """Solve a formula using the appropriate logical system."""
    
    # Auto-detect system if not specified
    if system is None:
        system = SystemSelector.detect_system([formula])
    
    # Translate if needed
    if system == LogicalSystem.ACRQ:
        translator = ACrQTranslator()
        formula = translator.translate_to_acrq(formula)
        
        # Use ACrQ tableau
        signed_formula = SignedFormula(sign, formula)
        tableau = ACrQTableau([signed_formula])
    else:
        # Use standard wKrQ tableau
        signed_formula = SignedFormula(sign, formula)
        tableau = Tableau([signed_formula])
    
    return tableau.construct()

def entails_acrq(premises: List[Formula], conclusion: Formula,
                 system: Optional[LogicalSystem] = None) -> bool:
    """Check entailment in the appropriate logical system."""
    
    all_formulas = premises + [conclusion]
    
    # Auto-detect system
    if system is None:
        system = SystemSelector.detect_system(all_formulas)
    
    # Translate if needed
    if system == LogicalSystem.ACRQ:
        translator = ACrQTranslator()
        premises = [translator.translate_to_acrq(p) for p in premises]
        conclusion = translator.translate_to_acrq(conclusion)
    
    # Standard entailment check
    from .formula import Conjunction, Negation
    
    if not premises:
        return valid(conclusion)
    
    combined_premises = premises[0]
    for p in premises[1:]:
        combined_premises = Conjunction(combined_premises, p)
    
    test_formula = Conjunction(combined_premises, Negation(conclusion))
    result = solve_acrq(test_formula, T, system)
    
    return not result.satisfiable
```

## Tableau Rules for ACrQ

### Bilateral Predicate Rules

#### True Sign Rules

```
T: R(a)                     T: R*(a)
───────                     ────────
T: R(a)                     F: R(a)
F: R*(a)                    T: R*(a)
```

#### False Sign Rules

```
F: R(a)                     F: R*(a)
───────────────             ───────────────
T: R*(a) │ N: R(a)         T: R(a) │ N: R(a)
         │ N: R*(a)                │ N: R*(a)
```

#### M Sign Rules (Meaningful)

```
M: R(a)
─────────────────
M: R(a) │ F: R(a)
        │ F: R*(a)
```

#### N Sign Rules (Neither/Undefined)

```
N: R(a)
───────
F: R(a)
F: R*(a)
```

### Negation with Bilateral Predicates

```
T: ¬R(a)        F: ¬R(a)        M: ¬R(a)        N: ¬R(a)
────────        ────────        ────────        ────────
T: R*(a)        F: R*(a)        M: R*(a)        N: R*(a)
```

### Closure Conditions (Extended)

A branch closes when:
1. **Standard contradiction**: `T: φ` and `F: φ` appear
2. **Bilateral contradiction**: `T: R(a)` and `T: R*(a)` appear
3. **Sign contradiction**: Any formula appears with incompatible signs

## Migration Path

### Phase 1: Non-Breaking Extension (Current wKrQ Preserved)

1. Add bilateral predicate classes alongside existing predicates
2. Extend formula hierarchy without modifying existing classes
3. Create ACrQTableau as subclass of Tableau
4. Add new API functions (solve_acrq, entails_acrq) without changing existing ones

### Phase 2: Unified System

1. Add system parameter to existing API functions
2. Auto-detect when ACrQ is needed based on formula content
3. Provide translation utilities for converting between systems
4. Update documentation with ACrQ examples

### Phase 3: Full Integration

1. Refactor Tableau to support pluggable rule systems
2. Create unified model extraction supporting both systems
3. Optimize shared components for both wKrQ and ACrQ
4. Add configuration for default system selection

## Testing Strategy

### Unit Tests

```python
class TestBilateralPredicates:
    """Test bilateral predicate functionality."""
    
    def test_bilateral_creation(self):
        """Test creating bilateral predicates."""
        pred = BilateralPredicateFormula("R", "R*", [Constant("a")])
        assert str(pred) == "R(a)"
        assert str(pred.get_dual()) == "R*(a)"
    
    def test_bilateral_consistency(self):
        """Test bilateral truth value consistency."""
        # This should raise an error
        with pytest.raises(ValueError):
            BilateralTruthValue(TRUE, TRUE)
    
    def test_bilateral_contradiction_detection(self):
        """Test that T:R(a) and T:R*(a) close a branch."""
        r_a = PredicateFormula("R", [Constant("a")])
        r_star_a = PredicateFormula("R*", [Constant("a")])
        
        tableau = ACrQTableau([
            SignedFormula(T, r_a),
            SignedFormula(T, r_star_a)
        ])
        
        result = tableau.construct()
        assert not result.satisfiable
```

### Integration Tests

```python
class TestACrQReasoning:
    """Test ACrQ reasoning capabilities."""
    
    def test_relevance_reasoning(self):
        """Test basic relevance logic reasoning."""
        # If R is relevant to S, and R(a), then we can derive something about S
        # This would use ACrQ's bilateral predicates to express relevance
        pass
    
    def test_translation_round_trip(self):
        """Test translating between wKrQ and ACrQ."""
        translator = ACrQTranslator()
        
        # Original wKrQ formula: ¬R(a)
        original = Negation(PredicateFormula("R", [Constant("a")]))
        
        # Translate to ACrQ: R*(a)
        acrq = translator.translate_to_acrq(original)
        assert isinstance(acrq, BilateralPredicateFormula)
        assert acrq.is_negative
        
        # Translate back: ¬R(a)
        back = translator.translate_from_acrq(acrq)
        assert back == original
```

### Validation Tests

```python
class TestFergusonACrQExamples:
    """Test examples from Ferguson 2021 paper."""
    
    def test_definition_17_translation(self):
        """Test Ferguson's Definition 17 translation examples."""
        # Test specific examples from the paper
        pass
    
    def test_lemma_5_closure(self):
        """Test Lemma 5 closure conditions."""
        # Test that branches close appropriately
        pass
    
    def test_lemma_6_reduction(self):
        """Test Lemma 6 showing ACrQ reduces to AC."""
        # Test the reduction property
        pass
```

## Future Considerations

### Performance Optimizations

1. **Bilateral Index**: Maintain index of R/R* pairs for O(1) contradiction detection
2. **Rule Caching**: Cache applicable rules for bilateral predicates
3. **Lazy Translation**: Only translate formulas when needed
4. **Parallel Branches**: Process bilateral branches in parallel

### Extensions

1. **SrQ Support**: Add system for S¹ᵢₐ with intentional contexts
2. **Hybrid Reasoning**: Allow mixing wKrQ and ACrQ in same proof
3. **Relevance Metrics**: Quantify degree of relevance between predicates
4. **Explanation Generation**: Explain why formulas are/aren't relevant

### Research Applications

1. **Belief Revision**: Model belief systems with relevance
2. **Knowledge Representation**: Express domain-specific relevance
3. **Natural Language**: Model conversational relevance
4. **AI Safety**: Reason about relevant/irrelevant AI behaviors

## Conclusion

The ACrQ extension provides a principled way to add relevance reasoning to our wKrQ implementation while maintaining backward compatibility. The bilateral predicate approach elegantly captures Angell's intuitions about analytic containment while preserving the computational efficiency of our tableau system.

The phased implementation strategy ensures we can incrementally add ACrQ features without disrupting existing functionality, making this a low-risk, high-reward enhancement to the wKrQ system.