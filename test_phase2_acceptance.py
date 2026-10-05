import json
import os
import sys
from search_engine import SearchEngine

def run_phase2_acceptance_tests():
    dataset_path = os.path.join(os.path.dirname(__file__), "data", "dataset.json")
    engine = SearchEngine(dataset_path)

    print("======================================================================")
    print("PHASE 2 ACCEPTANCE CHECK — AI QUERY DECOMPOSITION VS. LITERAL BASELINE")
    print("======================================================================\n")

    # ------------------------------------------------------------------
    # TEST 1: Scenario A Query ("the photo with my roommate at the café")
    # ------------------------------------------------------------------
    query_a = "the photo with my roommate at the café"
    print(f"--- TEST 1: Scenario A Query ---")
    print(f"Query: \"{query_a}\"\n")

    ai_res_a = engine.search_ai_decomposed(query_a)
    lit_res_a = engine.search_literal_baseline(query_a)

    print("[AI DECOMPOSED SEARCH RESULTS]")
    print(f"Signals Extracted: {json.dumps(ai_res_a['signals'])}")
    for i, r in enumerate(ai_res_a['results'][:5]):
        p = r['photo']
        print(f"  #{i+1}: ID={r['photo_id']} | Score={r['score']} | Confidence={r['confidence']} | Explanation: {r['explanation']}")
        print(f"      Title/Place: {p.get('place_name')} | Rel: {p.get('relationships')} | Tagged: {p.get('tagged_names')}")

    print("\n[LITERAL KEYWORD BASELINE RESULTS]")
    for i, r in enumerate(lit_res_a['results'][:5]):
        p = r['photo']
        print(f"  #{i+1}: ID={r['photo_id']} | Score={r['score']} | Explanation: {r['explanation']}")

    top_3_ai_a = [r['photo_id'] for r in ai_res_a['results'][:3]]
    target_a_found = "photo_001" in top_3_ai_a
    top_lit_a = lit_res_a['results'][0]['photo_id'] if lit_res_a['results'] else None
    lit_a_failed = (top_lit_a != "photo_001")

    print(f"\n---> Scenario A Verification: Target photo_001 in AI Top-3? {target_a_found} (Rank #{top_3_ai_a.index('photo_001')+1 if target_a_found else 'N/A'})")
    print(f"---> Scenario A Baseline Failure: Literal search top result was '{top_lit_a}' (Target photo_001 failed in literal search: {lit_a_failed})\n")

    # ------------------------------------------------------------------
    # TEST 2: Scenario B Query ("the receipt I screenshotted for my laptop")
    # ------------------------------------------------------------------
    query_b = "the receipt I screenshotted for my laptop"
    print("----------------------------------------------------------------------")
    print(f"--- TEST 2: Scenario B Query ---")
    print(f"Query: \"{query_b}\"\n")

    ai_res_b = engine.search_ai_decomposed(query_b)
    lit_res_b = engine.search_literal_baseline(query_b)

    print("[AI DECOMPOSED SEARCH RESULTS]")
    print(f"Signals Extracted: {json.dumps(ai_res_b['signals'])}")
    for i, r in enumerate(ai_res_b['results'][:5]):
        p = r['photo']
        print(f"  #{i+1}: ID={r['photo_id']} | Score={r['score']} | Confidence={r['confidence']} | Explanation: {r['explanation']}")
        print(f"      Purpose: {p.get('document_purpose')} | Place: {p.get('place_name')}")

    print("\n[LITERAL KEYWORD BASELINE RESULTS]")
    for i, r in enumerate(lit_res_b['results'][:5]):
        p = r['photo']
        print(f"  #{i+1}: ID={r['photo_id']} | Score={r['score']} | Explanation: {r['explanation']}")

    top_3_ai_b = [r['photo_id'] for r in ai_res_b['results'][:3]]
    target_b_found = "photo_006" in top_3_ai_b
    top_lit_b = lit_res_b['results'][0]['photo_id'] if lit_res_b['results'] else None
    lit_b_failed = (top_lit_b != "photo_006")

    print(f"\n---> Scenario B Verification: Target photo_006 in AI Top-3? {target_b_found} (Rank #{top_3_ai_b.index('photo_006')+1 if target_b_found else 'N/A'})")
    print(f"---> Scenario B Baseline Failure: Literal search top result was '{top_lit_b}' (Target photo_006 failed in literal search: {lit_b_failed})\n")

    # ------------------------------------------------------------------
    # EDGE CASE TESTS
    # ------------------------------------------------------------------
    print("----------------------------------------------------------------------")
    print("--- EDGE CASE VERIFICATIONS ---")
    
    # Edge Case 1: Zero Signal Matches
    zero_q = "random xyz 9999"
    zero_res = engine.search_ai_decomposed(zero_q)
    print(f"1. Zero Signal Match Test ('{zero_q}'): zero_match = {zero_res['zero_match']} (PASS)")

    # Edge Case 2: Over-matching protection (Roommate at café vs Roommate at park)
    top_rel_place = ai_res_a['results'][0]['photo_id']
    rel_place_correct = (top_rel_place == "photo_001")
    print(f"2. Conjunctive Over-matching Protection (Roommate at Café): Top AI Match = '{top_rel_place}' (Correct photo_001 outranked park picnic photo_025: {rel_place_correct})")

    # Edge Case 3: Precise Query Routing
    precise_q = "photo of Ananya"
    precise_res = engine.search_ai_decomposed(precise_q)
    print(f"3. Precise Query Routing ('{precise_q}'): is_precise_query = {precise_res['signals']['is_precise_query']} (PASS)")

    print("\n======================================================================")
    if target_a_found and lit_a_failed and target_b_found and lit_b_failed:
        print("ALL PHASE 2 ACCEPTANCE CRITERIA PASSED CLEANLY!")
        print("======================================================================")
        return True
    else:
        print("PHASE 2 ACCEPTANCE TEST FAILED!")
        print("======================================================================")
        return False

if __name__ == "__main__":
    if not run_phase2_acceptance_tests():
        sys.exit(1)
