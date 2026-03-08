"""
Explanation Facility - Generates human-readable reasoning traces.
"""

from dataclasses import dataclass

from knowledge_engineering.fact_base import FactBase
from knowledge_engineering.inference_engine import InferenceResult, MatchedRule, PartialMatch
from knowledge_engineering.rule_base import RuleCondition


@dataclass
class ExplanationEntry:
    """Structured explanation for a matched or partial rule."""
    section_id: str
    description: str
    specificity_score: int
    matched_facts: list[dict]  # [{unit, operator, expected, actual}]
    missing_facts: list[dict]  # [{unit, operator, expected}]


class ExplanationFacility:
    """Generates structured and human-readable explanations."""
    
    def generate(self, result: InferenceResult, fact_base: FactBase) -> list[ExplanationEntry]:
        """
        Create structured explanation entries for all matched and partial rules.
        
        Args:
            result: The inference result
            fact_base: The fact base used for inference
            
        Returns:
            List of explanation entries
        """
        entries = []
        
        # Explain matched rules
        for matched in result.matched_rules:
            matched_facts = []
            for condition in matched.matched_conditions:
                actual_value = fact_base.get(condition.knowledge_unit)
                matched_facts.append({
                    "unit": condition.knowledge_unit,
                    "operator": condition.operator,
                    "expected": condition.expected_value,
                    "actual": actual_value
                })
            
            entries.append(ExplanationEntry(
                section_id=matched.section_id,
                description=matched.description,
                specificity_score=matched.specificity_score,
                matched_facts=matched_facts,
                missing_facts=[]
            ))
        
        # Explain partial matches
        for partial in result.partial_matches:
            matched_facts = []
            for condition in partial.matched_conditions:
                actual_value = fact_base.get(condition.knowledge_unit)
                matched_facts.append({
                    "unit": condition.knowledge_unit,
                    "operator": condition.operator,
                    "expected": condition.expected_value,
                    "actual": actual_value
                })
            
            missing_facts = []
            for condition in partial.unmatched_conditions:
                missing_facts.append({
                    "unit": condition.knowledge_unit,
                    "operator": condition.operator,
                    "expected": condition.expected_value
                })
            
            entries.append(ExplanationEntry(
                section_id=partial.section_id,
                description=partial.description,
                specificity_score=len(partial.matched_conditions),
                matched_facts=matched_facts,
                missing_facts=missing_facts
            ))
        
        return entries
    
    def format_text(self, entries: list[ExplanationEntry]) -> str:
        """
        Format explanation entries as a human-readable string.
        
        Args:
            entries: List of explanation entries
            
        Returns:
            Formatted explanation text
        """
        if not entries:
            return "No rules matched the provided facts."
        
        lines = []
        
        # Separate matched and partial
        matched = [e for e in entries if not e.missing_facts]
        partial = [e for e in entries if e.missing_facts]
        
        if matched:
            lines.append("=== MATCHED IPC SECTIONS ===\n")
            for entry in matched:
                lines.append(f"Section {entry.section_id}: {entry.description}")
                lines.append(f"Specificity Score: {entry.specificity_score}")
                lines.append("Reasoning:")
                for fact in entry.matched_facts:
                    lines.append(f"  ✓ {fact['unit']} {fact['operator']} {fact['expected']} (actual: {fact['actual']})")
                lines.append("")
        
        if partial:
            lines.append("=== PARTIAL MATCHES ===\n")
            for entry in partial:
                lines.append(f"Section {entry.section_id}: {entry.description}")
                lines.append("Matched conditions:")
                for fact in entry.matched_facts:
                    lines.append(f"  ✓ {fact['unit']} {fact['operator']} {fact['expected']}")
                lines.append("Missing conditions:")
                for fact in entry.missing_facts:
                    lines.append(f"  ✗ {fact['unit']} {fact['operator']} {fact['expected']}")
                lines.append("")
        
        return "\n".join(lines)
