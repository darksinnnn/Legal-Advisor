"""
KE API - Flask REST API for the IPC Knowledge Engineering system.

Endpoints:
  POST /analyze       - Analyze case facts and return matched IPC sections
  GET  /sections      - List all available IPC section IDs
  GET  /sections/<id> - Get conditions for a specific section
"""

import os
import json

from flask import Flask, request, jsonify
from flask_cors import CORS

from knowledge_engineering.fact_base import FactBase
from knowledge_engineering.rule_base import RuleBase, RuleCondition, LegalRule
from knowledge_engineering.inference_engine import InferenceEngine
from knowledge_engineering.explanation import ExplanationFacility
from knowledge_engineering.rag_module import RAGModule


def _load_seed_rules() -> RuleBase:
    """Load seed rules from comprehensive_ipc_rules.json."""
    rules_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "comprehensive_ipc_rules.json"
    )
    rule_base = RuleBase()

    if not os.path.exists(rules_path):
        print(f"WARNING: Seed rules not found at {rules_path}")
        return rule_base

    with open(rules_path, "r", encoding="utf-8") as f:
        rules_dict = json.load(f)

    for section_id, rule_data in rules_dict.items():
        rule = RuleBase._dict_to_rule(rule_data)
        rule_base.add_rule(rule)

    print(f"Loaded {len(rule_base.list_section_ids())} seed rules")
    return rule_base


def create_app(rule_base: RuleBase | None = None, rag_module: RAGModule | None = None) -> Flask:
    """
    Create and configure the Flask app.

    Args:
        rule_base: Pre-loaded RuleBase (loads seed rules if None)
        rag_module: Pre-loaded RAGModule (creates new one if None)
    """
    app = Flask(__name__)
    CORS(app)

    rb = rule_base or _load_seed_rules()
    rag = rag_module if rag_module is not None else RAGModule()
    explanation_facility = ExplanationFacility()

    @app.route("/analyze", methods=["POST"])
    def analyze():
        """Analyze case facts and return matched IPC sections with explanations."""
        data = request.get_json(silent=True)

        if data is None or not isinstance(data, dict):
            return jsonify({"error": "Request body must be a JSON object"}), 400

        facts_raw = data.get("facts")
        if facts_raw is None or not isinstance(facts_raw, dict):
            return jsonify({"error": "'facts' must be a non-empty JSON object"}), 400

        if len(facts_raw) == 0:
            return jsonify({"error": "'facts' must be a non-empty JSON object"}), 400

        # Validate fact keys are strings
        for key in facts_raw:
            if not isinstance(key, str) or not key:
                return jsonify({"error": f"Fact keys must be non-empty strings, got: {key!r}"}), 400

        # Build fact base
        fact_base = FactBase()
        for name, value in facts_raw.items():
            if not isinstance(value, (bool, str)):
                return jsonify({"error": f"Fact '{name}' has unsupported type {type(value).__name__}. Use bool or str."}), 400
            fact_base.add(name, value)

        # Run inference
        engine = InferenceEngine(rb)
        result = engine.evaluate(fact_base)

        # Generate explanations
        entries = explanation_facility.generate(result, fact_base)

        # Retrieve supporting text from RAG
        warnings = []
        supporting_text = {}

        if rag.is_available():
            section_ids = [m.section_id for m in result.matched_rules]
            if section_ids:
                supporting_text = rag.retrieve(section_ids, k=3)
        else:
            warnings.append("FAISS vector database is unavailable. Returning inference results without supporting text.")

        # Build response
        matched_sections = [
            {
                "section_id": m.section_id,
                "description": m.description,
                "matched_conditions": [c.knowledge_unit for c in m.matched_conditions],
                "specificity_score": m.specificity_score,
            }
            for m in result.matched_rules
        ]

        partial_matches = [
            {
                "section_id": p.section_id,
                "description": p.description,
                "matched_conditions": [c.knowledge_unit for c in p.matched_conditions],
                "unmatched_conditions": [c.knowledge_unit for c in p.unmatched_conditions],
            }
            for p in result.partial_matches
        ]

        explanations = [
            {
                "section_id": e.section_id,
                "description": e.description,
                "specificity_score": e.specificity_score,
                "matched_facts": e.matched_facts,
                "missing_facts": e.missing_facts,
            }
            for e in entries
        ]

        return jsonify({
            "matched_sections": matched_sections,
            "partial_matches": partial_matches,
            "explanations": explanations,
            "supporting_text": supporting_text,
            "warnings": warnings,
        })

    @app.route("/sections", methods=["GET"])
    def list_sections():
        """Return all available IPC section IDs."""
        return jsonify({"sections": rb.list_section_ids()})

    @app.route("/sections/<section_id>", methods=["GET"])
    def get_section(section_id: str):
        """Return conditions for a specific IPC section."""
        rule = rb.get_rule(section_id)
        if rule is None:
            return jsonify({"error": "Section not found"}), 404

        conditions = [
            {
                "knowledge_unit": c.knowledge_unit,
                "operator": c.operator,
                "expected_value": c.expected_value,
            }
            for c in rule.conditions
        ]

        return jsonify({
            "section_id": rule.section_id,
            "description": rule.description,
            "conditions": conditions,
        })

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
