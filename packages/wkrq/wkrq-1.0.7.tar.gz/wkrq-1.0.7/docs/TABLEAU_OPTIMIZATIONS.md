# Tableau Calculus Optimizations

This document captures legitimate optimization techniques for semantic tableau theorem proving based on academic literature research.

## Research Summary

Our investigation revealed that "subsumption" as commonly understood in resolution theorem proving is NOT a standard optimization in basic tableau calculus. Instead, tableau literature focuses on different optimization approaches.

## Legitimate Tableau Optimizations from Literature

### 1. Branch Pruning
- **Source**: Multiple papers on semantic tableau optimizations
- **Description**: Eliminate branches that become contradictory or irrelevant
- **Quote**: "all branches containing one of the βj are pruned, that is, the effects of the β-rule application are undone"
- **Implementation**: When a branch closes, prune related branches

### 2. Simplification Rules  
- **Source**: Tableau optimization literature
- **Description**: Replace subformulas with true/false when context allows
- **Quote**: "for each prepositional formula ψ present on a branch B each positive occurrence of ψ as a subformula can soundly be replaced by true while each negative occurrence can be replaced by false"
- **Benefits**: "an inexpensive operation and can be computed in (low) polynomial time"

### 3. Intermediate Simplification
- **Source**: Massacci [1998b] and other optimization papers
- **Description**: Simplify formulas during tableau construction, not just at the end
- **Benefits**: Reduces search space significantly

### 4. Connectedness Restrictions
- **Source**: Wikipedia article on analytic tableaux, connection-based optimizations
- **Description**: Restrict expansion based on literal connections
- **Types**: Strong and weak connectedness conditions
- **Result**: "connectedness eliminates some possible choices of expansion, thus reducing search"

### 5. Formula Elimination via Splitting
- **Source**: ScienceDirect overview
- **Description**: Use clause splitting combined with elimination
- **Quote**: "Splitting on clauses is formally a combination of splitting and subsumption, where the original clause is eliminated via subsumption after the case split"
- **Note**: This is different from general subsumption - it's specific to clause-based tableaux

## What We Incorrectly Tried to Implement

### Resolution-Style Subsumption
- **Problem**: We tried to import clause subsumption from resolution theorem proving
- **Why it doesn't fit**: Formula-based tableaux work differently than clause-based resolution
- **Literature gap**: Standard tableau texts (Beth, Smullyan) don't emphasize general subsumption

### Backwards Formula Relationships  
- **Problem**: We confused which formulas should eliminate which
- **Root cause**: Mixing resolution terminology with tableau semantics

## Recommended Implementation Priorities

1. **Immediate**: Remove all subsumption code
2. **Short-term**: Implement simplification rules for obvious cases (true/false replacement)
3. **Medium-term**: Add branch pruning for contradictory paths
4. **Long-term**: Consider connectedness restrictions for first-order tableaux

## Key Papers Referenced
- "Simplifying and generalizing formulae in tableaux. Pruning the search space and building models" - SpringerLink
- Massacci [1998b] on intermediate simplification benefits
- Various ScienceDirect articles on tableau optimizations
- Wikipedia article on Method of analytic tableaux

## Implementation Notes

### Current wKrQ Architecture Compatibility
- **Branch structure**: Well-suited for branch pruning
- **Formula indexing**: Good foundation for simplification rules  
- **Three-valued logic**: May need special handling in optimizations
- **Quantifier handling**: Must preserve instantiation correctness

### Performance Considerations
- Simplification rules are polynomial time
- Branch pruning reduces exponential growth
- Connectedness restrictions require careful implementation to maintain completeness

## Anti-Patterns to Avoid
1. Don't implement resolution-style subsumption in formula-based tableaux
2. Don't eliminate formulas based purely on logical implication without considering branching behavior
3. Don't optimize without understanding the specific tableau variant (signed, unsigned, etc.)

---

*This document was compiled during the debugging of an incorrect subsumption implementation in wKrQ, January 2025.*