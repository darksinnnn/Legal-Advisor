"""
Basic tests to verify the system works correctly.
"""

import pytest
from knowledge_engineering.fact_base import FactBase
from knowledge_engineering.rule_base import RuleBase, LegalRule, RuleCondition
from knowledge_engineering.inference_engine import InferenceEngine
from knowledge_engineering.explanation import ExplanationFacility


def test_fact_base_basic():
    """Test basic fact base operations."""
    fb = FactBase()
    
    # Add facts
    fb.add("test_fact", True)
    fb.add("property_type", "movable")
    
    # Retrieve
    assert fb.get("test_fact") == True
    assert fb.get("property_type") == "movable"
    assert fb.get("nonexistent") is None
    
    # Update
    fb.add("test_fact", False)
    assert fb.get("test_fact") == False
    
    # Has
    assert fb.has("test_fact") == True
    assert fb.has("nonexistent") == False
    
    # List all
    all_facts = fb.list_all()
    assert len(all_facts) == 2
    
    # Clear
    fb.clear()
    assert len(fb.list_all()) == 0


def test_rule_base_basic():
    """Test basic rule base operations."""
    rb = RuleBase()
    
    # Create a simple rule
    rule = LegalRule(
        section_id="378",
        description="Theft",
        conditions=[
            RuleCondition("dishonest_intention", "equals", True),
            RuleCondition("property_type", "equals", "movable")
        ]
    )
    
    # Add rule
    rb.add_rule(rule)
    
    # Retrieve
    retrieved = rb.get_rule("378")
    assert retrieved is not None
    assert retrieved.section_id == "378"
    assert len(retrieved.conditions) == 2
    
    # List sections
    sections = rb.list_section_ids()
    assert "378" in sections
    
    # Remove
    assert rb.remove_rule("378") == True
    assert rb.get_rule("378") is None


def test_rule_validation():
    """Test rule validation."""
    rb = RuleBase()
    
    # Empty section_id should fail
    with pytest.raises(ValueError):
        rule = LegalRule(
            section_id="",
            description="Test",
            conditions=[RuleCondition("test", "equals", True)]
        )
        rb.add_rule(rule)
    
    # No conditions should fail
    with pytest.raises(ValueError):
        rule = LegalRule(
            section_id="123",
            description="Test",
            conditions=[]
        )
        rb.add_rule(rule)


def test_inference_basic():
    """Test basic inference."""
    rb = RuleBase()
    
    # Add a simple rule
    rule = LegalRule(
        section_id="378",
        description="Theft",
        conditions=[
            RuleCondition("dishonest_intention", "equals", True),
            RuleCondition("property_type", "equals", "movable")
        ]
    )
    rb.add_rule(rule)
    
    # Create matching facts
    fb = FactBase()
    fb.add("dishonest_intention", True)
    fb.add("property_type", "movable")
    
    # Run inference
    engine = InferenceEngine(rb)
    result = engine.evaluate(fb)
    
    # Should match
    assert len(result.matched_rules) == 1
    assert result.matched_rules[0].section_id == "378"
    assert result.matched_rules[0].specificity_score == 2


def test_inference_partial_match():
    """Test partial match detection."""
    rb = RuleBase()
    
    rule = LegalRule(
        section_id="378",
        description="Theft",
        conditions=[
            RuleCondition("dishonest_intention", "equals", True),
            RuleCondition("property_type", "equals", "movable"),
            RuleCondition("owner_consent", "equals", False)
        ]
    )
    rb.add_rule(rule)
    
    # Only provide 2 out of 3 facts
    fb = FactBase()
    fb.add("dishonest_intention", True)
    fb.add("property_type", "movable")
    
    engine = InferenceEngine(rb)
    result = engine.evaluate(fb)
    
    # Should not fully match
    assert len(result.matched_rules) == 0
    
    # Should partially match
    assert len(result.partial_matches) == 1
    assert result.partial_matches[0].section_id == "378"
    assert len(result.partial_matches[0].matched_conditions) == 2
    assert len(result.partial_matches[0].unmatched_conditions) == 1


def test_inference_operators():
    """Test different operators."""
    rb = RuleBase()
    
    # Test equals
    rule1 = LegalRule(
        section_id="1",
        description="Test equals",
        conditions=[RuleCondition("fact1", "equals", True)]
    )
    
    # Test not_equals
    rule2 = LegalRule(
        section_id="2",
        description="Test not_equals",
        conditions=[RuleCondition("fact2", "not_equals", False)]
    )
    
    # Test exists
    rule3 = LegalRule(
        section_id="3",
        description="Test exists",
        conditions=[RuleCondition("fact3", "exists", None)]
    )
    
    # Test in
    rule4 = LegalRule(
        section_id="4",
        description="Test in",
        conditions=[RuleCondition("fact4", "in", ["option1", "option2"])]
    )
    
    rb.add_rule(rule1)
    rb.add_rule(rule2)
    rb.add_rule(rule3)
    rb.add_rule(rule4)
    
    fb = FactBase()
    fb.add("fact1", True)
    fb.add("fact2", True)  # not_equals False, so True matches
    fb.add("fact3", "anything")  # exists, value doesn't matter
    fb.add("fact4", "option1")  # in list
    
    engine = InferenceEngine(rb)
    result = engine.evaluate(fb)
    
    # All should match
    assert len(result.matched_rules) == 4


def test_forward_chaining():
    """Test forward chaining with derived facts."""
    rb = RuleBase()
    
    # Rule 1: derives a fact
    rule1 = LegalRule(
        section_id="378",
        description="Theft",
        conditions=[
            RuleCondition("dishonest_intention", "equals", True),
            RuleCondition("property_type", "equals", "movable")
        ],
        derived_facts={"theft_established": True}
    )
    
    # Rule 2: triggered by derived fact
    rule2 = LegalRule(
        section_id="379",
        description="Punishment for theft",
        conditions=[
            RuleCondition("theft_established", "equals", True)
        ]
    )
    
    rb.add_rule(rule1)
    rb.add_rule(rule2)
    
    # Only provide initial facts
    fb = FactBase()
    fb.add("dishonest_intention", True)
    fb.add("property_type", "movable")
    
    engine = InferenceEngine(rb)
    result = engine.evaluate(fb)
    
    # Both rules should match (forward chaining)
    assert len(result.matched_rules) == 2
    section_ids = [r.section_id for r in result.matched_rules]
    assert "378" in section_ids
    assert "379" in section_ids


def test_exception_handling():
    """Test exception conditions."""
    rb = RuleBase()
    
    rule = LegalRule(
        section_id="378",
        description="Theft",
        conditions=[
            RuleCondition("dishonest_intention", "equals", True),
            RuleCondition("property_type", "equals", "movable")
        ],
        exceptions=[
            RuleCondition("good_faith_claim", "equals", True)
        ]
    )
    rb.add_rule(rule)
    
    # Case 1: No exception
    fb = FactBase()
    fb.add("dishonest_intention", True)
    fb.add("property_type", "movable")
    
    engine = InferenceEngine(rb)
    result = engine.evaluate(fb)
    assert len(result.matched_rules) == 1
    
    # Case 2: Exception triggered
    fb.add("good_faith_claim", True)
    result = engine.evaluate(fb)
    assert len(result.matched_rules) == 0  # Exception blocks the match


def test_conflict_resolution():
    """Test specificity-based conflict resolution."""
    rb = RuleBase()
    
    # Rule with 2 conditions
    rule1 = LegalRule(
        section_id="1",
        description="Less specific",
        conditions=[
            RuleCondition("fact1", "equals", True),
            RuleCondition("fact2", "equals", True)
        ]
    )
    
    # Rule with 4 conditions
    rule2 = LegalRule(
        section_id="2",
        description="More specific",
        conditions=[
            RuleCondition("fact1", "equals", True),
            RuleCondition("fact2", "equals", True),
            RuleCondition("fact3", "equals", True),
            RuleCondition("fact4", "equals", True)
        ]
    )
    
    rb.add_rule(rule1)
    rb.add_rule(rule2)
    
    # Provide all facts
    fb = FactBase()
    fb.add("fact1", True)
    fb.add("fact2", True)
    fb.add("fact3", True)
    fb.add("fact4", True)
    
    engine = InferenceEngine(rb)
    result = engine.evaluate(fb)
    
    # Both match, but more specific should come first
    assert len(result.matched_rules) == 2
    assert result.matched_rules[0].section_id == "2"  # More specific
    assert result.matched_rules[0].specificity_score == 4
    assert result.matched_rules[1].section_id == "1"  # Less specific
    assert result.matched_rules[1].specificity_score == 2


def test_explanation_generation():
    """Test explanation generation."""
    rb = RuleBase()
    
    rule = LegalRule(
        section_id="378",
        description="Theft",
        conditions=[
            RuleCondition("dishonest_intention", "equals", True),
            RuleCondition("property_type", "equals", "movable")
        ]
    )
    rb.add_rule(rule)
    
    fb = FactBase()
    fb.add("dishonest_intention", True)
    fb.add("property_type", "movable")
    
    engine = InferenceEngine(rb)
    result = engine.evaluate(fb)
    
    explainer = ExplanationFacility()
    explanations = explainer.generate(result, fb)
    
    assert len(explanations) == 1
    assert explanations[0].section_id == "378"
    assert len(explanations[0].matched_facts) == 2
    assert len(explanations[0].missing_facts) == 0
    
    # Test text formatting
    text = explainer.format_text(explanations)
    assert "378" in text
    assert "Theft" in text


def test_serialization():
    """Test JSON serialization round-trip."""
    rb = RuleBase()
    
    rule = LegalRule(
        section_id="378",
        description="Theft",
        conditions=[
            RuleCondition("dishonest_intention", "equals", True),
            RuleCondition("property_type", "equals", "movable")
        ],
        exceptions=[
            RuleCondition("good_faith_claim", "equals", True)
        ],
        derived_facts={"theft_established": True}
    )
    rb.add_rule(rule)
    
    # Serialize
    json_str = rb.to_json()
    
    # Deserialize
    rb2 = RuleBase.from_json(json_str)
    
    # Verify
    rule2 = rb2.get_rule("378")
    assert rule2 is not None
    assert rule2.section_id == "378"
    assert rule2.description == "Theft"
    assert len(rule2.conditions) == 2
    assert len(rule2.exceptions) == 1
    assert rule2.derived_facts["theft_established"] == True
