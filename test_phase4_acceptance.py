import urllib.request
import urllib.parse
import json
import os
import sys

def test_phase4_acceptance():
    print("======================================================================")
    print("PHASE 4 ACCEPTANCE CHECK — FEATURE 2 CLARIFYING QUESTION & REFINE FLOW")
    print("======================================================================\n")

    base_url = "http://localhost:8000"

    # 1. Ambiguous Query Trigger Check
    q_ambig = "photo from a trip"
    url_1 = f"{base_url}/api/search?q={urllib.parse.quote(q_ambig)}&mode=ai"
    req_1 = urllib.request.urlopen(url_1)
    data_1 = json.loads(req_1.read().decode("utf-8"))

    print(f"--- 1. Ambiguous Query Initial Search: \"{q_ambig}\" ---")
    print(f"Is Ambiguous Triggered? {data_1['is_ambiguous']}")
    print(f"Candidate Match Count: {data_1['total_matches']}")
    if data_1['is_ambiguous']:
        cq = data_1['clarifying_question']
        print(f"Generated Question: \"{cq['question']}\"")
        print(f"Options Presented: {cq['options']}")
    
    pass_trigger = data_1['is_ambiguous'] and (data_1['clarifying_question'] is not None)
    print(f"--> Ambiguity Trigger Pass? {pass_trigger} (Exactly 1 question generated)\n")

    # 2. Answering Question with Option Refinement ("Goa Beach Resort")
    refinement_option = "Goa Beach Resort"
    url_2 = f"{base_url}/api/search?q={urllib.parse.quote(q_ambig)}&mode=ai&refinement={urllib.parse.quote(refinement_option)}"
    req_2 = urllib.request.urlopen(url_2)
    data_2 = json.loads(req_2.read().decode("utf-8"))

    print(f"--- 2. Answering Clarifying Question with Refinement: \"{refinement_option}\" ---")
    print(f"Is Ambiguous Loop Triggered? {data_2['is_ambiguous']} (Must be False!)")
    print(f"Narrowed Match Count: {data_2['total_matches']}")
    narrowed_ids = [r['photo_id'] for r in data_2['results']]
    print(f"Narrowed Photo IDs: {narrowed_ids}")
    
    pass_answer = (not data_2['is_ambiguous']) and ("photo_011" in narrowed_ids) and (data_2['total_matches'] < data_1['total_matches'])
    print(f"--> Answering Refinement Pass? {pass_answer} (Shortlist measurably narrowed to Goa target photos)\n")

    # 3. Dismissing / Skipping Clarifying Question
    url_3 = f"{base_url}/api/search?q={urllib.parse.quote(q_ambig)}&mode=ai&skip=true"
    req_3 = urllib.request.urlopen(url_3)
    data_3 = json.loads(req_3.read().decode("utf-8"))

    print(f"--- 3. Dismissing / Skipping Clarifying Question (skip=true) ---")
    print(f"Is Ambiguous Loop Triggered? {data_3['is_ambiguous']} (Must be False!)")
    print(f"Skipped Status: {data_3['skipped']}")
    print(f"Returned Shortlist Item Count: {len(data_3['results'][:8])}")

    pass_skip = (not data_3['is_ambiguous']) and data_3['skipped'] and (len(data_3['results'][:8]) > 0)
    print(f"--> Skip Path Pass? {pass_skip} (Dismissing question returns usable shortlist without blocking)\n")

    # 4. Unmapped / Unhelpful Answer Loop Prevention Check
    unmapped_text = "random xyz 123 unmapped phrase"
    url_4 = f"{base_url}/api/search?q={urllib.parse.quote(q_ambig)}&mode=ai&refinement={urllib.parse.quote(unmapped_text)}"
    req_4 = urllib.request.urlopen(url_4)
    data_4 = json.loads(req_4.read().decode("utf-8"))

    print(f"--- 4. Unmapped Answer Edge Case: \"{unmapped_text}\" ---")
    print(f"Is Ambiguous Second Loop Triggered? {data_4['is_ambiguous']} (Must be False — strict 1-turn limit!)")
    print(f"Has Refinement: {data_4['has_refinement']}")
    
    pass_no_loop = (not data_4['is_ambiguous']) and data_4['has_refinement']
    print(f"--> 1-Turn Maximum Limit Pass? {pass_no_loop} (System does NOT loop a second question)\n")

    print("======================================================================")
    if pass_trigger and pass_answer and pass_skip and pass_no_loop:
        print("ALL PHASE 4 ACCEPTANCE CRITERIA PASSED CLEANLY!")
        print("======================================================================")
        return True
    else:
        print("PHASE 4 ACCEPTANCE TEST FAILED!")
        print("======================================================================")
        return False

if __name__ == "__main__":
    if not test_phase4_acceptance():
        sys.exit(1)
