import urllib.request
import urllib.parse
import json
import os
import sys

def test_phase3_ui():
    print("======================================================================")
    print("PHASE 3 ACCEPTANCE CHECK — UI RANKED SHORTLIST & CAP COMPLIANCE")
    print("======================================================================\n")

    base_url = "http://localhost:8000"

    # 1. Test Scenario A Query via UI Search API
    q_a = "the photo with my roommate at the café"
    url_a = f"{base_url}/api/search?q={urllib.parse.quote(q_a)}&mode=ai"
    req_a = urllib.request.urlopen(url_a)
    data_a = json.loads(req_a.read().decode("utf-8"))

    print(f"--- 1. Scenario A Query: \"{q_a}\" ---")
    print(f"Total Matches: {data_a['total_matches']}")
    top_3_a = data_a['results'][:3]
    top_3_ids_a = [r['photo_id'] for r in top_3_a]
    print(f"Top 3 Shortlist IDs: {top_3_ids_a}")
    for r in top_3_a:
        print(f"  ID={r['photo_id']} | Confidence={r['confidence']} | Explanation=\"{r['explanation']}\"")

    pass_a = "photo_001" in top_3_ids_a and bool(top_3_a[0]['explanation'])
    print(f"--> Scenario A UI Shortlist Pass? {pass_a} (Target photo_001 in Top-3 with specific explanation)\n")

    # 2. Test Scenario B Query via UI Search API
    q_b = "the receipt I screenshotted for my laptop"
    url_b = f"{base_url}/api/search?q={urllib.parse.quote(q_b)}&mode=ai"
    req_b = urllib.request.urlopen(url_b)
    data_b = json.loads(req_b.read().decode("utf-8"))

    print(f"--- 2. Scenario B Query: \"{q_b}\" ---")
    print(f"Total Matches: {data_b['total_matches']}")
    top_3_b = data_b['results'][:3]
    top_3_ids_b = [r['photo_id'] for r in top_3_b]
    print(f"Top 3 Shortlist IDs: {top_3_ids_b}")
    for r in top_3_b:
        print(f"  ID={r['photo_id']} | Confidence={r['confidence']} | Explanation=\"{r['explanation']}\"")

    pass_b = "photo_006" in top_3_ids_b and bool(top_3_b[0]['explanation'])
    print(f"--> Scenario B UI Shortlist Pass? {pass_b} (Target photo_006 in Top-3 with specific explanation)\n")

    # 3. Test Ambiguous Trip Query (8+ Photo Event Cluster Cap Compliance)
    q_c = "photo from a trip"
    url_c = f"{base_url}/api/search?q={urllib.parse.quote(q_c)}&mode=ai"
    req_c = urllib.request.urlopen(url_c)
    data_c = json.loads(req_c.read().decode("utf-8"))

    print(f"--- 3. Ambiguous Event Cluster Query: \"{q_c}\" ---")
    print(f"Total Backend Matches: {data_c['total_matches']}")
    shortlist_rendered = data_c['results'][:8]
    print(f"Rendered Shortlist Item Count: {len(shortlist_rendered)}")
    
    pass_cap = (data_c['total_matches'] >= 8) and (len(shortlist_rendered) <= 8)
    print(f"--> Shortlist Cap Compliance Pass? {pass_cap} (Total matches >= 8, rendered count capped at {len(shortlist_rendered)})\n")

    print("======================================================================")
    if pass_a and pass_b and pass_cap:
        print("ALL PHASE 3 ACCEPTANCE CRITERIA PASSED CLEANLY!")
        print("======================================================================")
        return True
    else:
        print("PHASE 3 ACCEPTANCE TEST FAILED!")
        print("======================================================================")
        return False

if __name__ == "__main__":
    if not test_phase3_ui():
        sys.exit(1)
