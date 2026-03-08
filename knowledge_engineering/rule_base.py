"""
Rule Base - Stores and manages IPC legal rules.
"""

import json
from dataclasses import dataclass, field, asdict
from typing import Literal

from knowledge_engineering.fact_base import FactValue

Operator = Literal["equals", "not_equals", "in", "exists"]


@dataclass
class RuleCondition:
    """A single testable condition within a legal rule."""
    knowledge_unit: str
    operator: Operator
    expected_value: FactValue | list[str] | None = None


@dataclass
class LegalRule:
    """An IF-THEN structure encoding an IPC section."""
    section_id: str
    description: str
    conditions: list[RuleCondition]
    exceptions: list[RuleCondition] = field(default_factory=list)
    derived_facts: dict[str, FactValue] = field(default_factory=dict)


class RuleBase:
    """Stores and manages a collection of legal rules."""
    
    def __init__(self):
        self._rules: dict[str, LegalRule] = {}
    
    def add_rule(self, rule: LegalRule) -> None:
        """
        Add or replace a rule.
        
        Args:
            rule: The legal rule to add
            
        Raises:
            ValueError: If rule has no conditions or empty section_id
        """
        if not rule.section_id or not isinstance(rule.section_id, str):
            raise ValueError("Rule must have a non-empty section_id")
        
        if not rule.conditions or len(rule.conditions) == 0:
            raise ValueError("Rule must have at least one condition")
        
        self._rules[rule.section_id] = rule
    
    def remove_rule(self, section_id: str) -> bool:
        """
        Remove a rule by section ID.
        
        Args:
            section_id: The section identifier
            
        Returns:
            True if the rule existed and was removed, False otherwise
        """
        if section_id in self._rules:
            del self._rules[section_id]
            return True
        return False
    
    def get_rule(self, section_id: str) -> LegalRule | None:
        """
        Retrieve a rule by section ID.
        
        Args:
            section_id: The section identifier
            
        Returns:
            The legal rule, or None if not found
        """
        return self._rules.get(section_id)
    
    def list_section_ids(self) -> list[str]:
        """Return all section IDs."""
        return list(self._rules.keys())
    
    def all_rules(self) -> list[LegalRule]:
        """Return all rules."""
        return list(self._rules.values())
    
    def to_json(self) -> str:
        """Serialize the entire rule base to JSON."""
        rules_dict = {
            section_id: self._rule_to_dict(rule)
            for section_id, rule in self._rules.items()
        }
        return json.dumps(rules_dict, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> "RuleBase":
        """Deserialize a rule base from JSON."""
        rule_base = cls()
        rules_dict = json.loads(json_str)
        
        for section_id, rule_data in rules_dict.items():
            rule = cls._dict_to_rule(rule_data)
            rule_base.add_rule(rule)
        
        return rule_base
    
    @staticmethod
    def _rule_to_dict(rule: LegalRule) -> dict:
        """Convert a LegalRule to a dictionary."""
        return {
            "section_id": rule.section_id,
            "description": rule.description,
            "conditions": [
                {
                    "knowledge_unit": c.knowledge_unit,
                    "operator": c.operator,
                    "expected_value": c.expected_value
                }
                for c in rule.conditions
            ],
            "exceptions": [
                {
                    "knowledge_unit": e.knowledge_unit,
                    "operator": e.operator,
                    "expected_value": e.expected_value
                }
                for e in rule.exceptions
            ],
            "derived_facts": rule.derived_facts
        }
    
    @staticmethod
    def _dict_to_rule(data: dict) -> LegalRule:
        """Convert a dictionary to a LegalRule."""
        return LegalRule(
            section_id=data["section_id"],
            description=data["description"],
            conditions=[
                RuleCondition(
                    knowledge_unit=c["knowledge_unit"],
                    operator=c["operator"],
                    expected_value=c.get("expected_value")
                )
                for c in data["conditions"]
            ],
            exceptions=[
                RuleCondition(
                    knowledge_unit=e["knowledge_unit"],
                    operator=e["operator"],
                    expected_value=e.get("expected_value")
                )
                for e in data.get("exceptions", [])
            ],
            derived_facts=data.get("derived_facts", {})
        )
