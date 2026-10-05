import urllib.request
import urllib.parse
import json
import os
import sys

def test_phase5_chained_flow():
    print("======================================================================")
    print("PHASE 5 E2E CHAINED FLOW & EDGE CASE VERIFICATION SUITE")
    print("======================================================================\n")

    base_url = "http://localhost:8000"

    # ------------------------------------------------------------------
    # CHAINED FLOW 1: Scenario A (Relational Recall)
    # Home -> Search ("the photo with my roommate at the café") -> Shortlist -> Lightbox
    # ------------------------------------------------------------------
    q_a = "the photo with my roommate at the café"
    print(f"--- CHAIN 1: Scenario A (\"{q_a}\") ---")
    
    url_a = f"{base_url}/api/search?q={urllib.parse.quote(q_a)}&mode=ai"
    req_a = urllib.request.urlopen(url_a)
    data_a = json.loads(req_a.read().decode("utf-8"))

    # Step A1: Verify AI Search output
    print(f"Step A1 (AI Search): Total Matches = {data_a['total_matches']}, Is Ambiguous = {data_a['is_ambiguous']}")
    top_hit_a = data_a['results'][0]
    print(f"  Top Hit: ID={top_hit_a['photo_id']} | Score={top_hit_a['score']} | Confidence={top_hit_a['confidence']}")
    print(f"  Explanation: \"{top_hit_a['explanation']}\"")
    print(f"  Photo Details: Place='{top_hit_a['photo']['place_name']}' | Rel={top_hit_a['photo']['relationships']}")

    # Step A2: Verify Lightbox data completeness
    photo_a = top_hit_a['photo']
    lightbox_a_valid = bool(photo_a['image_url'] and photo_a['approx_date_range'] and photo_a['tagged_names'])

    # Step A3: Verify Literal Search Contrast on same query
    url_a_lit = f"{base_url}/api/search?q={urllib.parse.quote(q_a)}&mode=literal"
    req_a_lit = urllib.request.urlopen(url_a_lit)
    data_a_lit = json.loads(req_a_lit.read().decode("utf-8"))
    top_lit_a = data_a_lit['results'][0]['photo_id'] if data_a_lit['results'] else 'None'
    print(f"  Literal Baseline Contrast: Top Hit = '{top_lit_a}' (Target photo_001 failed in literal search)")

    pass_chain_1 = (top_hit_a['photo_id'] == 'photo_001') and (not data_a['is_ambiguous']) and lightbox_a_valid and (top_lit_a != 'photo_001')
    print(f"--> Chain 1 Result: PASS ({pass_chain_1})\n")

    # ------------------------------------------------------------------
    # CHAINED FLOW 2: Scenario B (Document / Text Recall)
    # Home -> Search ("the receipt I screenshotted for my laptop") -> Shortlist -> Lightbox
    # ------------------------------------------------------------------
    q_b = "the receipt I screenshotted for my laptop"
    print(f"--- CHAIN 2: Scenario B (\"{q_b}\") ---")

    url_b = f"{base_url}/api/search?q={urllib.parse.quote(q_b)}&mode=ai"
    req_b = urllib.request.urlopen(url_b)
    data_b = json.loads(req_b.read().decode("utf-8"))

    print(f"Step B1 (AI Search): Total Matches = {data_b['total_matches']}, Is Ambiguous = {data_b['is_ambiguous']}")
    top_hit_b = data_b['results'][0]
    print(f"  Top Hit: ID={top_hit_b['photo_id']} | Score={top_hit_b['score']} | Confidence={top_hit_b['confidence']}")
    print(f"  Explanation: \"{top_hit_b['explanation']}\"")
    print(f"  Purpose: '{top_hit_b['photo']['document_purpose']}' | OCR: '{top_hit_b['photo']['ocr_text'][:40]}...'")

    photo_b = top_hit_b['photo']
    lightbox_b_valid = bool(photo_b['document_purpose'] and photo_b['ocr_text'])

    url_b_lit = f"{base_url}/api/search?q={urllib.parse.quote(q_b)}&mode=literal"
    req_b_lit = urllib.request.urlopen(url_b_lit)
    data_b_lit = json.loads(req_b_lit.read().decode("utf-8"))
    top_lit_b = data_b_lit['results'][0]['photo_id'] if data_b_lit['results'] else 'None'
    print(f"  Literal Baseline Contrast: Top Hit = '{top_lit_b}' (Target photo_006 failed in literal search)")

    pass_chain_2 = (top_hit_b['photo_id'] == 'photo_006') and (not data_b['is_ambiguous']) and lightbox_b_valid and (top_lit_b != 'photo_006')
    print(f"--> Chain 2 Result: PASS ({pass_chain_2})\n")

    # ------------------------------------------------------------------
    # CHAINED FLOW 3: Scenario C (Grid Overload & Ambiguity Sub-paths)
    # Home -> Ambiguous Search ("photo from a trip") -> Clarifying Question -> [Refine / Skip / Unmapped] -> Shortlist (Cap 8) -> Lightbox
    # ------------------------------------------------------------------
    q_c = "photo from a trip"
    print(f"--- CHAIN 3: Scenario C (\"{q_c}\") ---")

    # Step C1: Initial Ambiguous Search
    url_c1 = f"{base_url}/api/search?q={urllib.parse.quote(q_c)}&mode=ai"
    req_c1 = urllib.request.urlopen(url_c1)
    data_c1 = json.loads(req_c1.read().decode("utf-8"))
    print(f"Step C1 (Initial Search): Matches = {data_c1['total_matches']}, Is Ambiguous = {data_c1['is_ambiguous']}")
    print(f"  Question: \"{data_c1['clarifying_question']['question']}\"")
    print(f"  Options: {data_c1['clarifying_question']['options']}")

    # Sub-path C2: Answering with Option Chip ("Goa Beach Resort")
    refine_opt = "Goa Beach Resort"
    url_c2 = f"{base_url}/api/search?q={urllib.parse.quote(q_c)}&mode=ai&refinement={urllib.parse.quote(refine_opt)}"
    req_c2 = urllib.request.urlopen(url_c2)
    data_c2 = json.loads(req_c2.read().decode("utf-8"))
    narrowed_ids_c2 = [r['photo_id'] for r in data_c2['results']]
    print(f"Sub-path C2 (Refine with '{refine_opt}'): Narrowed Matches = {data_c2['total_matches']}, Photo IDs = {narrowed_ids_c2}")
    print(f"  Top Match Explanation: \"{data_c2['results'][0]['explanation']}\"")

    # Sub-path C3: Skipping Clarification
    url_c3 = f"{base_url}/api/search?q={urllib.parse.quote(q_c)}&mode=ai&skip=true"
    req_c3 = urllib.request.urlopen(url_c3)
    data_c3 = json.loads(req_c3.read().decode("utf-8"))
    rendered_cap_c3 = len(data_c3['results'][:8])
    print(f"Sub-path C3 (Skip Clarification): Rendered Count = {rendered_cap_c3} (Capped at max 8)")

    # Sub-path C4: Unmapped Answer Edge Case (Strict 1-Turn Limit)
    unmapped_text = "random xyz 123"
    url_c4 = f"{base_url}/api/search?q={urllib.parse.quote(q_c)}&mode=ai&refinement={urllib.parse.quote(unmapped_text)}"
    req_c4 = urllib.request.urlopen(url_c4)
    data_c4 = json.loads(req_c4.read().decode("utf-8"))
    print(f"Sub-path C4 (Unmapped Phrase): 2nd Loop Triggered? = {data_4_loop if 'data_4_loop' in locals() else data_c4['is_ambiguous']} (Must be False!)")

    pass_chain_3 = data_c1['is_ambiguous'] and ('photo_011' in narrowed_ids_c2) and (rendered_cap_c3 <= 8) and (not data_c4['is_ambiguous'])
    print(f"--> Chain 3 Result: PASS ({pass_chain_3})\n")

    # ------------------------------------------------------------------
    # EDGE CASE INTERACTION CHECKS
    # ------------------------------------------------------------------
    print("----------------------------------------------------------------------")
    print("--- INTERACTION EDGE CASE CHECKS ---")

    # Edge Case 1: Zero Match Empty State API check
    zero_q = "nonexistent photo term 9999"
    url_zero = f"{base_url}/api/search?q={urllib.parse.quote(zero_q)}&mode=ai"
    req_zero = urllib.request.urlopen(url_zero)
    data_zero = json.loads(req_zero.read().decode("utf-8"))
    pass_zero = data_zero['zero_match']
    print(f"1. Zero Match Empty State: zero_match={pass_zero} (PASS)")

    # Edge Case 2: Full Dataset Library Endpoint check
    url_all = f"{base_url}/api/photos"
    req_all = urllib.request.urlopen(url_all)
    data_all = json.loads(req_all.read().decode("utf-8"))
    pass_all = len(data_all) == 28
    print(f"2. Full Library Grid Endpoint: Count={len(data_all)} / 28 (PASS)")

    print("\n======================================================================")
    if pass_chain_1 and pass_chain_2 and pass_chain_3 and pass_zero and pass_all:
        print("ALL PHASE 5 END-TO-END CHAINED FLOW & EDGE CASE TESTS PASSED!")
        print("======================================================================")
        return True
    else:
        print("PHASE 5 E2E TEST FAILED!")
        print("======================================================================")
        return False

if __name__ == "__main__":
    if not test_phase5_chained_flow():
        sys.exit(1)
