import json
import os
import sys

def validate_dataset(filepath):
    print(f"--- Validating dataset: {filepath} ---")
    if not os.path.exists(filepath):
        print(f"FAIL: File {filepath} does not exist.")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            records = json.load(f)
        except Exception as e:
            print(f"FAIL: Invalid JSON format: {e}")
            return False

    print(f"Total Records: {len(records)}")
    if not (20 <= len(records) <= 30):
        print(f"FAIL: Record count ({len(records)}) is not between 20 and 30.")
        return False

    # Schema validation
    required_keys = {
        "photo_id": str,
        "image_url": str,
        "date_taken": str,
        "approx_date_range": str,
        "relationships": list,
        "tagged_names": list,
        "place_name": (str, type(None)),
        "visual_descriptors": list,
        "event_tags": list,
        "ocr_text": (str, type(None)),
        "document_purpose": (str, type(None))
    }

    ids = set()
    relational_count = 0
    document_count = 0
    event_tag_counts = {}
    place_null_count = 0
    place_populated_count = 0

    for i, r in enumerate(records):
        pid = r.get("photo_id")
        if not pid or pid in ids:
            print(f"FAIL: Record #{i} missing or duplicate photo_id '{pid}'")
            return False
        ids.add(pid)

        # Check required fields & types
        for key, expected_type in required_keys.items():
            if key not in r:
                print(f"FAIL: Record {pid} missing key '{key}'")
                return False
            val = r[key]
            if isinstance(expected_type, tuple):
                if not isinstance(val, expected_type):
                    print(f"FAIL: Record {pid} key '{key}' has invalid type {type(val)}")
                    return False
            else:
                if not isinstance(val, expected_type):
                    print(f"FAIL: Record {pid} key '{key}' has invalid type {type(val)}")
                    return False

        # Composition stats
        if len(r["relationships"]) > 0:
            relational_count += 1
        if r["document_purpose"] is not None:
            document_count += 1
        for et in r["event_tags"]:
            event_tag_counts[et] = event_tag_counts.get(et, 0) + 1
        if r["place_name"] is None:
            place_null_count += 1
        else:
            place_populated_count += 1

    print("\n--- Composition Summary ---")
    print(f"- Relational photos (relationships != []): {relational_count}")
    print(f"- Document photos (document_purpose != null): {document_count}")
    print(f"- Photos with populated place_name: {place_populated_count}")
    print(f"- Photos with null place_name: {place_null_count}")
    
    max_event_tag, max_event_count = max(event_tag_counts.items(), key=lambda x: x[1])
    print(f"- Largest event cluster: '{max_event_tag}' with {max_event_count} photos")

    # Composition checks
    if relational_count < 4:
        print(f"FAIL: Relational cluster requires at least 4 photos, found {relational_count}")
        return False
    if document_count < 4:
        print(f"FAIL: Document cluster requires at least 4 photos, found {document_count}")
        return False
    if max_event_count < 8:
        print(f"FAIL: Ambiguity event cluster requires at least 8 photos, found {max_event_count}")
        return False
    if place_null_count == 0 or place_populated_count == 0:
        print("FAIL: Dataset must have a mix of populated and null place_name values")
        return False

    # Check distractors
    distractor_ids = ["photo_020", "photo_021", "photo_022", "photo_023", "photo_024", "photo_025"]
    found_distractors = [p for p in records if p["photo_id"] in distractor_ids]
    print(f"- Verified adversarial near-miss distractors: {len(found_distractors)} / {len(distractor_ids)}")
    if len(found_distractors) < 6:
        print("FAIL: Missing required near-miss distractor records")
        return False

    print("\nSUCCESS: Dataset is valid and satisfies all PRD §5 & Implementation Phase 0 requirements!\n")
    return True

if __name__ == "__main__":
    path = os.path.join(os.path.dirname(__file__), "data", "dataset.json")
    if not validate_dataset(path):
        sys.exit(1)
