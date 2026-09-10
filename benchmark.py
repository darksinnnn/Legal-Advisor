"""
Performance Benchmark for IPC Legal Research Assistant.
Tests rule-based expert system accuracy against curated test cases.
Generates performance metrics, charts and tables.
"""

import sys
import os
import time
import json

project_root = os.path.dirname(os.path.abspath(__file__))
venv_site = os.path.join(project_root, "knowledge_engineering", "venv", "Lib", "site-packages")
if os.path.exists(venv_site) and venv_site not in sys.path:
    sys.path.insert(0, venv_site)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from knowledge_engineering.hybrid_system import HybridIPCSystem

# ── Ground-truth test cases ──────────────────────────────────────────
# Each case has a description and the expected IPC sections that SHOULD match.
TEST_CASES = [
    {
        "id": 1,
        "category": "Homicide",
        "description": "A man intentionally killed his neighbor with a knife after planning the murder for weeks.",
        "expected_sections": ["300", "302"],
        "expected_partial": ["307"],
    },
    {
        "id": 2,
        "category": "Negligence",
        "description": "A drunk driver was speeding on the highway and hit a pedestrian who later died in the hospital.",
        "expected_sections": ["304A"],
        "expected_partial": ["279"],
    },
    {
        "id": 3,
        "category": "Theft",
        "description": "Someone stole my laptop from my office without my permission when I was away.",
        "expected_sections": ["378", "379"],
        "expected_partial": [],
    },
    {
        "id": 4,
        "category": "Robbery",
        "description": "A group of people broke into my house at night, threatened me with a knife, and stole my jewelry.",
        "expected_sections": ["392", "397"],
        "expected_partial": ["390", "395"],
    },
    {
        "id": 5,
        "category": "Dowry",
        "description": "My husband and his family have been demanding dowry and torturing me since our marriage two years ago.",
        "expected_sections": ["498A"],
        "expected_partial": ["304B"],
    },
    {
        "id": 6,
        "category": "Forgery",
        "description": "Someone forged my signature on a property document and sold my land to another person.",
        "expected_sections": ["463", "464", "465", "467", "468"],
        "expected_partial": [],
    },
    {
        "id": 7,
        "category": "Acid Attack",
        "description": "A man threw acid on a woman after she rejected his proposal, causing severe burns on her face.",
        "expected_sections": ["326A", "326B"],
        "expected_partial": [],
    },
    {
        "id": 8,
        "category": "Defamation",
        "description": "Someone spread false rumors about me on social media that damaged my reputation in the community.",
        "expected_sections": ["499", "500"],
        "expected_partial": [],
    },
    {
        "id": 9,
        "category": "Kidnapping",
        "description": "My child was kidnapped from school and the kidnappers demanded a ransom of 10 lakhs.",
        "expected_sections": ["359", "363", "364A"],
        "expected_partial": [],
    },
    {
        "id": 10,
        "category": "Rioting",
        "description": "A mob of several people gathered and set fire to shops in the market using violence.",
        "expected_sections": ["147", "436"],
        "expected_partial": ["435", "148"],
    },
    {
        "id": 11,
        "category": "Cheating/Fraud",
        "description": "A con artist deceived my elderly mother by impersonating a bank official and stole her savings through a fake scheme.",
        "expected_sections": ["415", "416", "417", "419", "420"],
        "expected_partial": [],
    },
    {
        "id": 12,
        "category": "Criminal Breach of Trust",
        "description": "My business partner who was entrusted with company funds embezzled all the money and fled the country.",
        "expected_sections": ["405", "406"],
        "expected_partial": [],
    },
    {
        "id": 13,
        "category": "Wrongful Confinement",
        "description": "My employer locked me up in a room and did not allow me to leave for three days, holding me captive.",
        "expected_sections": ["340", "342"],
        "expected_partial": ["346"],
    },
    {
        "id": 14,
        "category": "Sexual Assault",
        "description": "A woman was sexually assaulted and raped by a man who broke into her house at night.",
        "expected_sections": ["375", "376"],
        "expected_partial": [],
    },
    {
        "id": 15,
        "category": "Criminal Conspiracy",
        "description": "Three men conspired together and planned to rob a bank, then jointly carried out the robbery.",
        "expected_sections": ["120A", "120B", "34"],
        "expected_partial": [],
    },
    {
        "id": 16,
        "category": "Trespass",
        "description": "A stranger secretly entered my house at night and was found lurking inside with intent to steal.",
        "expected_sections": ["441", "443", "444", "445", "446", "447", "448", "449", "456", "457"],
        "expected_partial": [],
    },
    {
        "id": 17,
        "category": "Hurt/Grievous Hurt",
        "description": "A man intentionally attacked another with an iron rod causing a broken arm and permanent disability.",
        "expected_sections": ["319", "320", "321", "323", "324", "325", "326"],
        "expected_partial": [],
    },
    {
        "id": 18,
        "category": "Stalking",
        "description": "A man has been repeatedly following and watching a woman despite her telling him she is not interested.",
        "expected_sections": ["354D"],
        "expected_partial": [],
    },
    {
        "id": 19,
        "category": "Mischief/Arson",
        "description": "Someone deliberately set fire to my house at night, destroying it completely.",
        "expected_sections": ["435", "436"],
        "expected_partial": ["425", "426"],
    },
    {
        "id": 20,
        "category": "Culpable Homicide",
        "description": "A man threw a heavy stone at another during a fight, knowing it could cause death. The victim died.",
        "expected_sections": ["299", "304"],
        "expected_partial": [],
    },
]


def evaluate_case(system, case):
    """Run a single test case and compute metrics."""
    start = time.perf_counter()
    results = system.analyze_case(case["description"])
    elapsed_ms = (time.perf_counter() - start) * 1000

    matched_ids = {s["section_id"] for s in results["matched_sections"]}
    partial_ids = {s["section_id"] for s in results["partial_matches"]}
    expected = set(case["expected_sections"])
    expected_partial = set(case.get("expected_partial", []))

    # Metrics
    true_positives = matched_ids & expected
    false_negatives = expected - matched_ids  # expected but not matched
    # Consider a section "found" if it appears in either full or partial
    found_anywhere = matched_ids | partial_ids
    coverage = len(expected & found_anywhere) / len(expected) if expected else 1.0

    precision = len(true_positives) / len(matched_ids) if matched_ids else (1.0 if not expected else 0.0)
    recall = len(true_positives) / len(expected) if expected else 1.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    # Partial match quality: how many expected partials were actually found as partial
    partial_found = partial_ids & expected_partial

    return {
        "id": case["id"],
        "category": case["category"],
        "expected": sorted(expected),
        "matched": sorted(matched_ids),
        "partial": sorted(partial_ids),
        "true_positives": sorted(true_positives),
        "false_negatives": sorted(false_negatives),
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "coverage": coverage,
        "num_matched": len(matched_ids),
        "num_partial": len(partial_ids),
        "num_facts": len([k for k, v in results["extracted_facts"].items() if v is True]),
        "time_ms": elapsed_ms,
    }


def run_benchmark():
    """Run all test cases and aggregate results."""
    print("=" * 70)
    print("  IPC Legal Research Assistant — Performance Benchmark")
    print("=" * 70)
    print("\nInitializing system...")
    
    system = HybridIPCSystem()
    
    print(f"\nRunning {len(TEST_CASES)} test cases...\n")
    
    all_results = []
    for case in TEST_CASES:
        result = evaluate_case(system, case)
        all_results.append(result)
        status = "PASS" if result["recall"] >= 0.5 else "WARN" if result["coverage"] >= 0.5 else "FAIL"
        print(f"  {status} Case {result['id']:2d} [{result['category']:<25s}] "
              f"P={result['precision']:.2f} R={result['recall']:.2f} F1={result['f1']:.2f} "
              f"Coverage={result['coverage']:.2f} "
              f"Matched={result['num_matched']} Partial={result['num_partial']} "
              f"Time={result['time_ms']:.1f}ms")

    # Aggregate
    avg_precision = sum(r["precision"] for r in all_results) / len(all_results)
    avg_recall = sum(r["recall"] for r in all_results) / len(all_results)
    avg_f1 = sum(r["f1"] for r in all_results) / len(all_results)
    avg_coverage = sum(r["coverage"] for r in all_results) / len(all_results)
    avg_time = sum(r["time_ms"] for r in all_results) / len(all_results)
    total_matched = sum(r["num_matched"] for r in all_results)
    total_partial = sum(r["num_partial"] for r in all_results)
    total_facts = sum(r["num_facts"] for r in all_results)

    print("\n" + "=" * 70)
    print("  AGGREGATE RESULTS")
    print("=" * 70)
    print(f"  Total Test Cases:      {len(all_results)}")
    print(f"  Avg Precision:         {avg_precision:.4f}")
    print(f"  Avg Recall:            {avg_recall:.4f}")
    print(f"  Avg F1 Score:          {avg_f1:.4f}")
    print(f"  Avg Coverage:          {avg_coverage:.4f}")
    print(f"  Avg Inference Time:    {avg_time:.2f} ms")
    print(f"  Total Rules Fired:     {total_matched}")
    print(f"  Total Partial Matches: {total_partial}")
    print(f"  Total Facts Extracted: {total_facts}")
    print("=" * 70)

    # Save JSON for chart generation
    output = {
        "results": all_results,
        "aggregate": {
            "num_cases": len(all_results),
            "avg_precision": avg_precision,
            "avg_recall": avg_recall,
            "avg_f1": avg_f1,
            "avg_coverage": avg_coverage,
            "avg_time_ms": avg_time,
            "total_matched": total_matched,
            "total_partial": total_partial,
            "total_facts": total_facts,
        }
    }
    out_path = os.path.join(project_root, "benchmark_results.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {out_path}")
    return output


if __name__ == "__main__":
    run_benchmark()
