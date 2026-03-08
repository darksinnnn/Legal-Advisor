"""
Hybrid IPC Legal Analysis System

Combines:
1. Keyword-based fact extraction from natural language case descriptions
2. Knowledge Engineering rule-based inference (158 IPC sections)
3. FAISS vector search (RAG) for supporting legal text retrieval
4. Explanation facility for transparent reasoning

Works for ANY case description and returns ALL applicable IPC sections.
"""

import os
import sys
import json
import re

# Ensure imports work from any working directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from knowledge_engineering.fact_base import FactBase
from knowledge_engineering.rule_base import RuleBase
from knowledge_engineering.inference_engine import InferenceEngine
from knowledge_engineering.explanation import ExplanationFacility
from knowledge_engineering.rag_module import RAGModule


# ---------------------------------------------------------------------------
# Comprehensive fact extraction patterns
# Each key is a knowledge_unit name used in the rule base.
# Each value is a list of keyword/phrase triggers.
# ---------------------------------------------------------------------------
FACT_PATTERNS: dict[str, list[str]] = {
    # --- Death / Homicide ---
    "caused_death": [
        "killed", "murdered", "caused death", "homicide", "slain",
        "shot dead", "stabbed to death", "beaten to death", "died",
        "death occurred", "lost life", "fatal",
    ],
    "intention_to_cause_death": [
        "intended to kill", "with intent to murder", "premeditated murder",
        "planned to kill", "deliberate killing", "wanted to kill",
    ],
    "knowledge_likely_to_cause_death": [
        "knew it could cause death", "likely to cause death",
        "reckless act causing death", "dangerous act",
    ],
    "attempt_to_murder": [
        "tried to kill", "attempt to murder", "attempted murder",
        "tried to murder", "attempted to kill",
    ],
    "attempt_to_cause_death": [
        "tried to kill", "attempt to cause death", "attempted to cause death",
    ],
    "victim_committed_suicide": [
        "committed suicide", "suicide", "took own life", "hanged himself",
        "hanged herself", "self-immolation",
    ],

    # --- Hurt / Injury ---
    "caused_hurt": [
        "hurt", "injured", "wounded", "beat", "beaten", "assault",
        "attacked", "hit", "struck", "punched", "kicked", "slapped",
        "bruised", "cut", "laceration", "bleeding",
    ],
    "grievous_hurt": [
        "grievous", "serious injury", "permanent damage", "broken bone",
        "fracture", "disfigure", "lost limb", "lost eye", "lost ear",
        "permanent disability", "severe injury", "acid",
    ],
    "voluntarily": [
        "intentionally", "voluntarily", "deliberately", "on purpose",
        "willfully", "knowingly",
    ],
    "use_of_weapon": [
        "weapon", "knife", "gun", "sword", "acid", "firearm", "pistol",
        "rifle", "sharp object", "iron rod", "stick", "bat", "axe",
        "dagger", "machete", "lathi", "rod",
    ],
    "acid_attack": [
        "acid attack", "threw acid", "acid thrown", "acid splash",
    ],
    "provocation": [
        "provoked", "provocation", "sudden provocation",
    ],
    "grave_sudden_provocation": [
        "grave and sudden provocation", "extreme provocation",
    ],
    "private_defense": [
        "self defense", "self-defense", "private defense", "private defence",
        "defending himself", "defending herself", "in defense",
    ],
    "endangered_life": [
        "endangered life", "risk to life", "life threatening",
        "danger to life",
    ],

    # --- Negligence ---
    "negligence": [
        "negligent", "careless", "reckless", "rash driving",
        "negligence", "rash and negligent", "rash", "irresponsible",
        "drunk driving", "speeding", "over-speeding",
    ],
    "rash_driving": [
        "rash driving", "reckless driving", "speeding", "drunk driving",
        "over-speeding", "dangerous driving", "drunk driver",
    ],

    # --- Property crimes ---
    "dishonest_intention": [
        "dishonest", "steal", "stole", "stolen", "theft", "thief",
        "took without permission", "misappropriat", "embezzle",
        "swindled", "pilfered", "sold my", "sold his", "sold her",
    ],
    "property_type": [
        # We set this to "movable" when movable property keywords match
    ],
    "moved_property": [
        "took", "taken", "stole", "grabbed", "snatched", "carried away",
        "removed property", "ran away with",
    ],
    "without_consent": [
        "without permission", "without consent", "forcibly",
        "against will", "unauthorized", "illegally", "unlawfully",
        "without authority",
    ],
    "property_in_possession": [
        "in possession", "had possession", "was holding", "entrusted",
        "was keeping", "was in charge of",
    ],
    "converted_to_own_use": [
        "converted to own use", "used for himself", "used for herself",
        "misappropriated", "embezzled", "pocketed",
    ],
    "entrusted_with_property": [
        "entrusted", "given charge", "handed over", "trusted with",
        "given custody", "fiduciary",
    ],
    "received_stolen_property": [
        "received stolen", "bought stolen", "accepted stolen",
        "knowingly received",
    ],
    "knowledge_of_stolen": [
        "knew it was stolen", "knowledge of stolen", "aware it was stolen",
    ],
    "concealed_stolen_property": [
        "concealed stolen", "hid stolen", "hidden stolen property",
    ],
    "concealed_property": [
        "concealed property", "hid property", "hidden assets",
    ],

    # --- Movable property detection ---
    "_movable_property_keywords": [
        "property", "belongings", "goods", "money", "cash", "valuables",
        "laptop", "phone", "jewel", "vehicle", "car", "bike", "watch",
        "gold", "silver", "ornament", "mobile", "purse", "wallet",
        "bag", "cattle", "animal",
    ],

    # --- Robbery / Dacoity ---
    "robbery": [
        "robbed", "robbery", "looted", "mugged", "snatched at gunpoint",
        "held up", "armed robbery",
    ],
    "attempted_robbery": [
        "attempted robbery", "tried to rob", "attempted to loot",
    ],
    "dacoity": [
        "dacoit", "dacoity", "gang robbery", "armed gang",
        "group robbery", "gang loot",
    ],
    "preparation_for_dacoity": [
        "preparing for dacoity", "planning robbery", "assembled for robbery",
    ],
    "five_or_more_persons": [
        "five or more", "group of five", "gang of", "large group",
        "mob of", "five people", "several people",
    ],

    # --- Extortion ---
    "extortion": [
        "extort", "blackmail", "demanded money", "pay or else",
        "threatened for money", "protection money", "ransom",
    ],

    # --- Trespass / House-breaking ---
    "entered_property": [
        "entered", "trespass", "broke into", "intruded",
        "entered house", "entered property", "entered land",
        "broke in", "barged in", "forced entry",
    ],
    "property_owned_by_other": [
        "my house", "my property", "my land", "my shop", "my office",
        "someone's", "another's", "neighbor's", "neighbour's",
        "his house", "her house", "their house", "our house",
    ],
    "in_dwelling_house": [
        "house", "home", "dwelling", "residence", "apartment", "flat",
        "room", "building",
    ],
    "house_breaking": [
        "broke into house", "house breaking", "forced entry",
        "broke the door", "broke the lock", "broke window",
        "smashed door", "smashed window",
    ],
    "night_time": [
        "night", "midnight", "after dark", "late night", "at night",
        "nighttime", "2 am", "3 am", "1 am",
    ],
    "concealed_trespass": [
        "sneaked in", "secretly entered", "hid inside", "lurking",
    ],

    # --- Mischief / Arson ---
    "mischief_to_property": [
        "damaged property", "destroyed property", "vandalized", "set fire",
        "arson", "broke window", "smashed", "defaced", "demolished",
        "damaged car", "damaged house", "damaged shop", "damaged vehicle",
    ],
    "intent_to_cause_damage": [
        "intent to damage", "deliberately damaged", "intentionally destroyed",
        "purposely broke", "maliciously damaged", "vandalized",
        "destroyed property", "set fire",
    ],
    "significant_damage": [
        "significant damage", "heavy damage", "extensive damage",
        "costly damage", "expensive",
    ],
    "arson": [
        "arson", "set fire", "burned", "burnt", "fire",
        "set ablaze", "torched", "firebombed",
    ],
    "target_is_dwelling": [
        "house", "home", "dwelling", "residence",
    ],
    "fire_involved": [
        "fire", "flame", "burning", "blaze",
    ],
    "explosive_substance": [
        "explosive", "bomb", "dynamite", "blast", "detonator",
    ],
    "killed_animal": [
        "killed animal", "killed cattle", "killed cow", "killed dog",
        "poisoned animal", "maimed animal",
    ],
    "damaged_water_supply": [
        "damaged water supply", "diverted water", "blocked canal",
        "damaged irrigation",
    ],

    # --- Threats / Intimidation ---
    "threat": [
        "threatened", "threat", "intimidat", "menace", "warned",
        "scared", "terrorized", "terrorised",
    ],
    "intent_to_intimidate": [
        "to scare", "to frighten", "to intimidate", "to threaten",
        "to coerce", "threatened", "intimidated",
    ],
    "anonymous_communication": [
        "anonymous", "anonymous letter", "anonymous call",
        "unknown number", "anonymous message",
    ],

    # --- Criminal force / Assault ---
    "criminal_force": [
        "pushed", "shoved", "dragged", "restrained", "confined",
        "locked up", "tied up", "grabbed", "manhandled",
    ],
    "assault": [
        "assaulted", "attacked", "hit", "struck", "punched",
        "kicked", "slapped", "beat",
    ],
    "use_of_force": [
        "force", "forcibly", "by force", "physical force",
        "violence", "violent", "use of force",
    ],

    # --- Wrongful restraint / Confinement ---
    "wrongful_restraint": [
        "restrained", "blocked path", "prevented from leaving",
        "stopped from going", "obstructed movement",
    ],
    "wrongful_confinement": [
        "confined", "locked up", "imprisoned", "detained",
        "held against will", "not allowed to leave", "captive",
        "held captive", "hostage",
    ],
    "secret_confinement": [
        "secretly confined", "hidden location", "secret place",
        "unknown location",
    ],

    # --- Sexual offences ---
    "sexual_assault": [
        "rape", "raped", "sexual assault", "molest", "molested",
        "sexual harassment", "outrage modesty", "touched inappropriately",
        "sexual abuse", "sexually assaulted",
    ],
    "sexual_harassment": [
        "sexual harassment", "sexually harassed", "inappropriate touching",
        "sexual remarks", "demanded sexual favours",
    ],
    "victim_is_woman": [
        "woman", "girl", "female", "wife", "daughter", "sister",
        "lady", "mother", "her", "my husband", "his wife",
        "bride", "married woman",
    ],
    "intent_to_outrage_modesty": [
        "outrage modesty", "outraged modesty", "modesty",
        "inappropriate touch", "groped",
    ],
    "intent_to_disrobe": [
        "disrobe", "tore clothes", "stripped", "removed clothes",
    ],
    "stalking": [
        "stalk", "stalked", "followed", "following", "watching",
        "harassing repeatedly", "cyber stalking",
    ],
    "voyeurism": [
        "voyeur", "peeping", "watching private", "recording private",
        "hidden camera", "spy camera",
    ],
    "insulted_modesty": [
        "insulted modesty", "eve teasing", "catcalling", "obscene gesture",
        "lewd remarks", "vulgar comments",
    ],

    # --- Kidnapping / Abduction ---
    "kidnapping": [
        "kidnap", "kidnapped", "abduct", "abducted", "taken away",
        "held captive", "hostage",
    ],
    "abduction": [
        "abducted", "abduction", "forcibly taken", "carried away by force",
    ],
    "ransom_demand": [
        "ransom", "demanded ransom", "pay ransom", "ransom money",
    ],
    "forced_marriage": [
        "forced marriage", "forced to marry", "compelled marriage",
    ],
    "victim_is_minor": [
        "child", "minor", "underage", "below 18", "kid", "infant",
        "baby", "juvenile", "boy", "young girl",
    ],
    "human_trafficking": [
        "trafficking", "trafficked", "human trafficking", "sold person",
        "bonded labour", "forced labour", "slave",
    ],
    "sold_for_prostitution": [
        "sold for prostitution", "forced into prostitution",
        "sex trafficking",
    ],
    "procuration": [
        "procured minor", "induced minor", "lured minor",
    ],

    # --- Cheating / Fraud ---
    "cheating": [
        "cheated", "fraud", "deceived", "tricked", "scam", "swindled",
        "duped", "conned", "defrauded", "forged", "sold my",
    ],
    "deception": [
        "deceived", "deception", "false representation", "lied",
        "misrepresented", "false promise", "fake", "forged",
    ],
    "induced_delivery": [
        "induced delivery", "made to hand over", "tricked into giving",
        "fraudulently obtained", "induced to deliver", "sold my",
        "sold his", "sold her",
    ],
    "impersonation": [
        "impersonat", "pretended to be", "posed as", "disguised as",
        "false identity", "fake identity",
    ],
    "breach_of_trust": [
        "breach of trust", "misused trust", "embezzle", "embezzled",
        "fiduciary duty", "betrayed trust",
    ],

    # --- Forgery ---
    "forgery": [
        "forged", "forgery", "fake document", "false document",
        "counterfeit", "fabricated document",
    ],
    "false_document": [
        "false document", "fake document", "forged document",
        "fabricated document", "fraudulent document",
        "forged", "forgery",
    ],
    "used_forged_document": [
        "used forged", "presented forged", "submitted fake",
    ],
    "knowledge_of_forgery": [
        "knew it was forged", "aware of forgery",
    ],
    "forged_valuable_security": [
        "forged cheque", "forged will", "forged deed", "forged bond",
        "forged property document",
    ],
    "counterfeiting": [
        "counterfeit", "fake currency", "duplicate notes",
    ],
    "currency_notes": [
        "currency", "bank notes", "rupee notes", "money notes",
    ],
    "used_counterfeit_currency": [
        "used fake currency", "passed counterfeit", "circulated fake notes",
    ],

    # --- Defamation ---
    "defamation": [
        "defam", "slander", "libel", "false accusation",
        "damaged reputation", "character assassination",
        "spread false rumors", "spread false rumours",
    ],
    "intent_to_harm_reputation": [
        "damage reputation", "harm reputation", "ruin reputation",
        "defame", "malign", "damaged reputation", "damaged my reputation",
        "false rumors", "false rumours", "spread rumors", "spread rumours",
    ],

    # --- Public order ---
    "rioting": [
        "riot", "rioting", "mob violence", "violent crowd",
        "group violence", "mob attack",
    ],
    "unlawful_assembly": [
        "unlawful assembly", "illegal gathering", "mob", "crowd gathered",
        "group assembled", "mob gathered",
    ],
    "affray": [
        "public fight", "fighting in public", "brawl", "affray",
    ],
    "public_nuisance": [
        "nuisance", "public disturbance", "noise pollution",
        "obstruction", "blocked road",
    ],
    "public_place": [
        "public place", "road", "street", "market", "park",
        "railway station", "bus stop", "public",
    ],
    "drunken_misconduct": [
        "drunk", "intoxicated", "drunken behavior", "drunken behaviour",
    ],

    # --- Common intention / Conspiracy ---
    "common_intention": [
        "together", "jointly", "common intention", "in furtherance",
        "all of them", "acting together",
    ],
    "multiple_persons": [
        "group", "gang", "several people", "multiple persons",
        "together", "jointly", "accomplice", "co-accused",
    ],
    "criminal_act_committed": [
        # This is derived — set to true when any crime fact is detected
    ],
    "criminal_conspiracy": [
        "conspir", "planned together", "plotted", "hatched plan",
        "colluded", "conspiracy",
    ],
    "criminal_intent": [
        "criminal intent", "malicious intent", "with intent",
    ],

    # --- Abetment ---
    "abetment": [
        "helped commit", "instigated", "aided", "abetted",
        "encouraged crime", "provoked to commit", "incited",
    ],

    # --- Government / Public servants ---
    "accused_is_public_servant": [
        "government official", "public servant", "police officer",
        "magistrate", "judge", "official",
    ],
    "victim_is_public_servant": [
        "police", "officer", "government official", "public servant",
        "magistrate",
    ],
    "impersonated_public_servant": [
        "pretended to be police", "fake police", "impersonated officer",
        "posed as official",
    ],
    "wore_uniform_of_public_servant": [
        "wore police uniform", "fake uniform", "wore official uniform",
    ],
    "obstruction_of_public_servant": [
        "obstructed police", "obstructed officer", "resisted police",
        "prevented officer",
    ],
    "disobeyed_law": [
        "disobeyed law", "violated law", "broke the law",
    ],
    "bribery": [
        "bribe", "corruption", "paid off", "illegal payment",
        "kickback", "gratification",
    ],
    "resisted_arrest": [
        "resisted arrest", "fled from police", "evaded arrest",
        "ran from police",
    ],

    # --- Evidence tampering ---
    "false_evidence": [
        "false evidence", "perjury", "lied in court", "false testimony",
    ],
    "judicial_proceeding": [
        "court", "judicial", "trial", "hearing", "proceeding",
    ],
    "induced_false_evidence": [
        "induced false evidence", "forced to lie", "threatened witness",
    ],
    "destroyed_evidence": [
        "destroyed evidence", "tampered evidence", "removed evidence",
    ],
    "destroyed_document": [
        "destroyed document", "shredded document", "burned document",
    ],
    "intent_to_prevent_evidence": [
        "to prevent evidence", "to hide evidence", "to destroy proof",
    ],
    "false_charge": [
        "false charge", "false case", "false FIR", "false complaint",
        "framed",
    ],
    "harboured_offender": [
        "harboured", "sheltered criminal", "hid the accused",
        "gave shelter to offender",
    ],
    "knowledge_of_offence": [
        "knew about the crime", "aware of offence", "knowledge of crime",
    ],
    "insulted_court": [
        "insulted court", "contempt of court", "disrupted court",
    ],

    # --- Marriage offences ---
    "bigamy": [
        "bigamy", "married again", "second marriage", "already married",
    ],
    "concealed_marriage": [
        "concealed marriage", "hid first marriage", "secret marriage",
    ],
    "adultery": [
        "adultery", "extramarital", "affair",
    ],
    "enticed_married_woman": [
        "enticed married woman", "lured married woman",
    ],
    "cruelty_by_husband_or_relatives": [
        "cruelty by husband", "domestic violence", "dowry harassment",
        "tortured by husband", "tortured by in-laws", "harassed by husband",
        "beaten by husband", "cruelty by in-laws",
        "torturing", "tortured", "harassed", "cruelty",
        "husband and his family", "in-laws", "husband",
    ],
    "dowry_demand": [
        "dowry", "dowry demand", "demanded dowry", "demanding dowry",
    ],
    "within_seven_years_of_marriage": [
        "within 7 years", "within seven years", "recently married",
        "soon after marriage", "since our marriage", "after marriage",
        "years ago", "year ago",
    ],
    "domestic_cruelty_established": [],

    # --- Religion ---
    "defiled_place_of_worship": [
        "defiled temple", "defiled mosque", "defiled church",
        "defiled gurudwara", "vandalized temple", "vandalized mosque",
    ],
    "intent_to_insult_religion": [
        "insult religion", "hurt religious sentiments",
        "offend religious feelings",
    ],
    "outraged_religious_feelings": [
        "outraged religious feelings", "hurt religious sentiments",
        "blasphemy",
    ],
    "wounded_religious_feelings": [
        "wounded religious feelings", "insulted religion",
    ],
    "deliberate_act": [
        "deliberately", "intentionally", "on purpose", "willfully",
    ],
    "promoted_enmity": [
        "promoted enmity", "incited hatred", "communal hatred",
        "hate speech",
    ],
    "between_groups": [
        "between communities", "between religions", "between castes",
        "communal",
    ],

    # --- Disease / Health ---
    "spread_disease": [
        "spread disease", "spread infection", "infected others",
        "contagious", "epidemic",
    ],
    "malignant_intent": [
        "malignant intent", "deliberately spread",
    ],
    "poisonous_substance": [
        "poison", "poisonous", "toxic substance",
    ],

    # --- Obscenity ---
    "obscene_material": [
        "obscene", "pornograph", "indecent material",
    ],
    "sale_or_distribution": [
        "sold", "distributed", "circulated", "published",
    ],

    # --- Election ---
    "election_related": [
        "election", "voting", "ballot", "poll",
    ],
    "undue_influence": [
        "undue influence", "coerced voter", "influenced voter",
    ],

    # --- Misc ---
    "preparation_for_violence": [
        "prepared weapon", "brought weapon", "armed themselves",
        "came prepared",
    ],
    "attempted_offence": [
        "attempted", "tried to", "attempt to",
    ],
    "fraudulent_intent": [
        "fraudulent", "fraud", "fraudulently",
    ],
}


class HybridIPCSystem:
    """
    Hybrid system that combines:
    - Keyword fact extraction from case descriptions
    - KE rule-based inference (158 IPC sections)
    - RAG retrieval from FAISS vector DB
    - Explanation facility

    Works for ANY case description. Returns ALL applicable IPC sections.
    """

    def __init__(self):
        """Initialize all components."""
        # Load rule base
        rules_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "comprehensive_ipc_rules.json",
        )
        self.rule_base = RuleBase()
        if os.path.exists(rules_path):
            with open(rules_path, "r", encoding="utf-8") as f:
                rules_dict = json.load(f)
            for _sid, rule_data in rules_dict.items():
                rule = RuleBase._dict_to_rule(rule_data)
                self.rule_base.add_rule(rule)
            print(f"Loaded {len(self.rule_base.list_section_ids())} IPC rules")

        # RAG module (graceful if FAISS unavailable)
        self.rag = RAGModule()
        if self.rag.is_available():
            print("FAISS vector database loaded")
        else:
            print("WARNING: FAISS database not available. Only rule-based reasoning will work.")

        self.explanation_facility = ExplanationFacility()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze_case(self, case_description: str, top_k: int = 10) -> dict:
        """
        Analyze a case description and return all applicable IPC sections.

        Pipeline:
        1. Extract facts from natural language
        2. Run KE inference (forward chaining over 158 rules)
        3. Retrieve supporting text via RAG
        4. Generate explanations

        Returns a dict with matched_sections, partial_matches, explanations,
        supporting_text, extracted_facts, and warnings.
        """
        warnings: list[str] = []

        # Step 1 — fact extraction
        fact_base = self._extract_facts(case_description)
        extracted = fact_base.list_all()

        # Step 2 — inference
        engine = InferenceEngine(self.rule_base)
        result = engine.evaluate(fact_base)

        # Step 3 — explanations
        entries = self.explanation_facility.generate(result, fact_base)

        # Step 4 — RAG supporting text
        supporting_text: dict[str, list[str]] = {}
        if self.rag.is_available():
            section_ids = [m.section_id for m in result.matched_rules]
            if section_ids:
                supporting_text = self.rag.retrieve(section_ids, k=3)
        else:
            warnings.append(
                "FAISS vector database unavailable — returning inference results without supporting text."
            )

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

        return {
            "case_description": case_description,
            "extracted_facts": extracted,
            "matched_sections": matched_sections,
            "partial_matches": partial_matches,
            "explanations": explanations,
            "supporting_text": supporting_text,
            "warnings": warnings,
        }

    # ------------------------------------------------------------------
    # Fact extraction
    # ------------------------------------------------------------------

    def _extract_facts(self, case_description: str) -> FactBase:
        """
        Extract legal facts from a natural language case description
        using keyword/phrase matching against FACT_PATTERNS.
        """
        text = case_description.lower()
        fb = FactBase()

        any_crime = False

        for fact_name, keywords in FACT_PATTERNS.items():
            # Skip internal helper keys
            if fact_name.startswith("_"):
                continue
            if not keywords:
                continue

            for kw in keywords:
                if kw in text:
                    fb.add(fact_name, True)
                    any_crime = True
                    break

        # Detect movable property → set property_type = "movable"
        for kw in FACT_PATTERNS.get("_movable_property_keywords", []):
            if kw in text:
                fb.add("property_type", "movable")
                break

        # If any crime-related fact was extracted, mark criminal_act_committed
        if any_crime:
            fb.add("criminal_act_committed", True)

        # Smart defaults for legal reasoning:
        # If death was caused by negligence but no intent to kill was detected,
        # explicitly set intention_to_cause_death = false so 304A can fire.
        if fb.has("caused_death") and fb.has("negligence") and not fb.has("intention_to_cause_death"):
            fb.add("intention_to_cause_death", False)

        # If hurt was caused but no explicit "voluntarily" keyword, check for
        # assault/attack keywords which imply voluntary action
        if fb.has("caused_hurt") and not fb.has("voluntarily"):
            if fb.has("assault") or fb.has("use_of_weapon") or fb.has("criminal_force"):
                fb.add("voluntarily", True)

        return fb

    # ------------------------------------------------------------------
    # Pretty-print
    # ------------------------------------------------------------------

    def print_analysis(self, results: dict) -> None:
        """Pretty-print analysis results to console."""
        print("\n" + "=" * 70)
        print("IPC LEGAL ANALYSIS REPORT")
        print("=" * 70)

        print(f"\nCase: {results['case_description']}")

        facts = results["extracted_facts"]
        fact_names = [k for k, v in facts.items() if v is True]
        print(f"\nExtracted Facts ({len(fact_names)}): {', '.join(fact_names)}")

        matched = results["matched_sections"]
        partial = results["partial_matches"]

        if matched:
            print(f"\n--- Fully Matched IPC Sections ({len(matched)}) ---\n")
            for i, s in enumerate(matched, 1):
                print(f"  {i}. Section {s['section_id']}: {s['description']}")
                print(f"     Specificity: {s['specificity_score']} | "
                      f"Conditions: {', '.join(s['matched_conditions'])}")
        else:
            print("\nNo fully matched IPC sections.")

        if partial:
            print(f"\n--- Partial Matches ({len(partial)}) ---\n")
            for s in partial[:10]:  # show top 10
                print(f"  Section {s['section_id']}: {s['description']}")
                print(f"     Matched: {', '.join(s['matched_conditions'])}")
                print(f"     Missing: {', '.join(s['unmatched_conditions'])}")

        if results.get("supporting_text"):
            print("\n--- Supporting Legal Text (from FAISS) ---\n")
            for sid, texts in results["supporting_text"].items():
                print(f"  Section {sid}:")
                for t in texts[:1]:
                    print(f"    {t[:200]}...")

        if results.get("warnings"):
            print("\n--- Warnings ---")
            for w in results["warnings"]:
                print(f"  ⚠ {w}")

        print("\n" + "=" * 70)


# ---------------------------------------------------------------------------
# CLI demo
# ---------------------------------------------------------------------------

def main():
    """Run demo with sample cases."""
    print("Initializing Hybrid IPC Legal Analysis System...")
    system = HybridIPCSystem()

    test_cases = [
        "A group of people entered my house without permission at night, "
        "threatened me with a knife, and stole my laptop and jewelry.",

        "Someone forged my signature on a property document and sold my land "
        "to another person.",

        "A man attacked a woman with acid after she rejected his proposal.",

        "My business partner embezzled company funds that were entrusted to him "
        "and fled the country.",

        "A mob gathered and set fire to several shops in the market.",

        "Someone spread false rumors about me on social media that damaged my "
        "reputation in the community.",

        "A drunk driver was speeding on the highway and hit a pedestrian who "
        "later died in the hospital.",

        "My husband and his family have been demanding dowry and torturing me "
        "since our marriage two years ago.",
    ]

    for case in test_cases:
        results = system.analyze_case(case)
        system.print_analysis(results)
        print("\n")


if __name__ == "__main__":
    main()
