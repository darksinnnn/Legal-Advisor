"""
Inference Engine - Forward chaining rule evaluation with conflict resolution.
"""

from dataclasses import dataclass
from typing import Set

from knowledge_engineering.fact_base import FactBase
from knowledge_engineering.rule_base import RuleBase, LegalRule, RuleCondition


@dataclass
class MatchedRule:
    """A rule that fully matched the facts."""
    section_id: str
    description: str
    matched_conditions: list[RuleCondition]
    specificity_score: int


@dataclass
class PartialMatch:
    """A rule that partially matched the facts."""
    section_id: str
    description: str
    matched_conditions: list[RuleCondition]
    unmatched_conditions: list[RuleCondition]


@dataclass
class InferenceResult:
    """Result of inference engine evaluation."""
    matched_rules: list[MatchedRule]
    partial_matches: list[PartialMatch]


class InferenceEngine:
    """Forward chaining inference engine with conflict resolution."""
    
    def __init__(self, rule_base: RuleBase):
        self._rule_base = rule_base
    
    def evaluate(self, fact_base: FactBase) -> InferenceResult:
        """
        Run forward chaining inference.
        
        1. Evaluate all rules against current facts
        2. Fire fully matched rules (no exception triggered)
        3. Assert derived facts from fired rules
        4. Repeat until no new facts are derived
        5. Rank matched rules by specificity (stable sort)
        6. Collect partial matches
        
        Args:
            fact_base: The fact base to evaluate against
            
        Returns:
            InferenceResult with matched and partial rules
        """
        matched_rules: list[MatchedRule] = []
        partial_matches: list[PartialMatch] = []
        fired_rules: Set[str] = set()
        
        # Forward chaining loop
        max_iterations = 100  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            new_facts_derived = False
            
            for rule in self._rule_base.all_rules():
                # Skip already fired rules
                if rule.section_id in fired_rules:
                    continue
                
                # Check if exceptions are triggered
                if self._check_exceptions(rule, fact_base):
                    continue
                
                # Evaluate conditions
                matched_conds, unmatched_conds = self._evaluate_rule(rule, fact_base)
                
                # Fully matched rule
                if len(unmatched_conds) == 0:
                    matched_rules.append(MatchedRule(
                        section_id=rule.section_id,
                        description=rule.description,
                        matched_conditions=matched_conds,
                        specificity_score=len(matched_conds)
                    ))
                    fired_rules.add(rule.section_id)
                    
                    # Assert derived facts
                    if rule.derived_facts:
                        for fact_name, fact_value in rule.derived_facts.items():
                            if not fact_base.has(fact_name):
                                fact_base.add(fact_name, fact_value)
                                new_facts_derived = True
                
                # Partially matched rule
                elif len(matched_conds) > 0:
                    partial_matches.append(PartialMatch(
                        section_id=rule.section_id,
                        description=rule.description,
                        matched_conditions=matched_conds,
                        unmatched_conditions=unmatched_conds
                    ))
            
            # Stop if no new facts were derived
            if not new_facts_derived:
                break
        
        # Conflict resolution: sort by specificity (descending), stable sort
        matched_rules.sort(key=lambda r: r.specificity_score, reverse=True)
        
        return InferenceResult(
            matched_rules=matched_rules,
            partial_matches=partial_matches
        )
    
    def _evaluate_rule(self, rule: LegalRule, fact_base: FactBase) -> tuple[list[RuleCondition], list[RuleCondition]]:
        """
        Evaluate all conditions of a rule.
        
        Returns:
            (matched_conditions, unmatched_conditions)
        """
        matched = []
        unmatched = []
        
        for condition in rule.conditions:
            if self._evaluate_condition(condition, fact_base):
                matched.append(condition)
            else:
                unmatched.append(condition)
        
        return matched, unmatched
    
    def _evaluate_condition(self, condition: RuleCondition, fact_base: FactBase) -> bool:
        """
        Evaluate a single condition against the fact base.
        
        Operators:
        - equals: fact value equals expected value
        - not_equals: fact value does not equal expected value
        - in: fact value is in the expected list
        - exists: fact exists (regardless of value)
        """
        fact_value = fact_base.get(condition.knowledge_unit)
        
        if condition.operator == "exists":
            return fact_value is not None
        
        if fact_value is None:
            return False
        
        if condition.operator == "equals":
            return fact_value == condition.expected_value
        
        if condition.operator == "not_equals":
            return fact_value != condition.expected_value
        
        if condition.operator == "in":
            if isinstance(condition.expected_value, list):
                return fact_value in condition.expected_value
            return False
        
        return False
    
    def _check_exceptions(self, rule: LegalRule, fact_base: FactBase) -> bool:
        """
        Check if any exception condition is satisfied.
        
        Returns:
            True if any exception is triggered (rule should be excluded)
        """
        for exception in rule.exceptions:
            if self._evaluate_condition(exception, fact_base):
                return True
        return False
