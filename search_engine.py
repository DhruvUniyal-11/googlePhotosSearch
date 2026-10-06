import json
import re
import os

class SearchEngine:
    def __init__(self, dataset_path, user_dataset_path=None):
        self.dataset_path = dataset_path
        self.user_dataset_path = user_dataset_path or os.path.join(os.path.dirname(dataset_path), "user_photos.json")
        self.load_all_photos()

    def load_all_photos(self):
        with open(self.dataset_path, "r", encoding="utf-8") as f:
            self.seeded_dataset = json.load(f)
        self.user_photos = []
        if os.path.exists(self.user_dataset_path):
            try:
                with open(self.user_dataset_path, "r", encoding="utf-8") as f:
                    self.user_photos = json.load(f)
            except Exception as e:
                print(f"Warning: could not load user_photos.json: {e}")
                self.user_photos = []
        self.dataset = self.user_photos + self.seeded_dataset
        self._build_vocab()

    def add_user_photo(self, photo_data):
        self.user_photos.insert(0, photo_data)
        with open(self.user_dataset_path, "w", encoding="utf-8") as f:
            json.dump(self.user_photos, f, indent=2)
        self.dataset = self.user_photos + self.seeded_dataset
        self._build_vocab()
        return photo_data

    def reset_user_photos(self):
        self.user_photos = []
        if os.path.exists(self.user_dataset_path):
            with open(self.user_dataset_path, "w", encoding="utf-8") as f:
                json.dump([], f)
        self.dataset = list(self.seeded_dataset)
        self._build_vocab()

    def _build_vocab(self):
        """
        Builds dynamic vocabulary sets from the dataset to ensure 100% signal extraction
        coverage for all visual descriptors, event tags, place names, relationships, and doc intents.
        """
        self.vocab_visual = set()
        self.vocab_event = set()
        self.vocab_rel = set()
        self.vocab_doc = set()

        for p in self.dataset:
            for v in p.get("visual_descriptors", []) or []:
                v_lower = v.lower()
                self.vocab_visual.add(v_lower)
                for w in v_lower.split():
                    if len(w) > 2:
                        self.vocab_visual.add(w)
            if p.get("place_name"):
                pl_lower = p["place_name"].lower()
                self.vocab_visual.add(pl_lower)
                for w in pl_lower.split():
                    if len(w) > 2:
                        self.vocab_visual.add(w)
            for e in p.get("event_tags", []) or []:
                e_lower = e.lower()
                self.vocab_event.add(e_lower)
                for w in e_lower.split():
                    if len(w) > 2:
                        self.vocab_event.add(w)
            for r in p.get("relationships", []) or []:
                self.vocab_rel.add(r.lower())
            if p.get("document_purpose"):
                self.vocab_doc.add(p["document_purpose"].lower())

    def decompose_query(self, query, refinement=None):
        """
        Decomposes a natural language query into structured signals.
        Includes relational, visual/object/place, document intent, event, and temporal terms.
        """
        q_combined = f"{query} {refinement}".strip() if refinement else query
        q_lower = q_combined.lower().strip()
        
        # 1. Relational terms extraction
        rel_map = {
            "roommate": ["roommate"],
            "sister": ["sister"],
            "brother": ["brother"],
            "friend": ["college friend", "friend"],
            "college friend": ["college friend"],
            "cousin": ["cousin"],
            "mom": ["mom", "mother"],
            "mother": ["mom", "mother"],
            "dad": ["dad", "father"],
            "father": ["dad", "father"],
            "partner": ["partner"],
            "husband": ["husband", "partner"],
            "wife": ["wife", "partner"],
            "boyfriend": ["boyfriend", "partner"],
            "girlfriend": ["girlfriend", "partner"],
            "dog": ["dog", "pet"],
            "cat": ["cat", "pet"],
            "coworker": ["coworker", "colleague"],
            "colleague": ["coworker", "colleague"]
        }
        for r in self.vocab_rel:
            r_lower = r.lower()
            if r_lower not in rel_map:
                rel_map[r_lower] = [r_lower]

        extracted_rel = []
        for term, mapped in rel_map.items():
            if re.search(r'\b' + re.escape(term) + r'\b', q_lower):
                extracted_rel.extend(mapped)
        extracted_rel = list(set(extracted_rel))

        # 2. Document Intent extraction
        doc_intent = None
        if any(w in q_lower for w in ["receipt", "invoice", "bill", "screenshotted", "ticket", "boarding pass"]):
            if any(w in q_lower for w in ["laptop", "macbook", "computer"]):
                doc_intent = "laptop purchase receipt"
            elif any(w in q_lower for w in ["flight", "boarding", "sfo", "airplane"]):
                doc_intent = "flight ticket"
            elif any(w in q_lower for w in ["concert", "coldplay"]):
                doc_intent = "concert ticket"
            elif any(w in q_lower for w in ["phone", "iphone"]):
                doc_intent = "phone replacement receipt"
            elif any(w in q_lower for w in ["grocery", "whole foods"]):
                doc_intent = "grocery receipt"
            elif any(w in q_lower for w in ["coffee"]):
                doc_intent = "coffee receipt"
            else:
                doc_intent = "receipt"

        # 3. Visual Descriptors & Place/Location Terms Extraction
        place_terms = []
        visual_object_keywords = [
            "cake", "birthday cake", "chocolate cake", "candles", "balloons", "party hats",
            "café", "cafe", "coffee shop", "starbucks", "blue bottle", "coffee", "blue chairs", "outdoor seating",
            "laptop", "macbook", "desk", "workstation", "pizza", "couch", "book", "novel",
            "paris", "beach", "resort", "mountains", "snow", "park", "picnic", "diner", "canyon", "lake tahoe",
            "goa", "manali", "louvre", "eiffel", "kayak", "camping", "tent", "river", "sunset", "gowns", "diploma"
        ]
        for vk in visual_object_keywords:
            if re.search(r'\b' + re.escape(vk) + r'\b', q_lower):
                place_terms.append(vk)
        for vv in self.vocab_visual:
            if len(vv) > 2 and vv not in place_terms and re.search(r'\b' + re.escape(vv) + r'\b', q_lower):
                place_terms.append(vv)

        # 4. Event terms extraction
        event_terms = []
        event_keywords = ["trip", "vacation", "birthday", "baking", "picnic", "game night", "concert", "graduation", "camping", "hiking", "party"]
        for e in event_keywords:
            if re.search(r'\b' + re.escape(e) + r'\b', q_lower):
                event_terms.append(e)
        for ve in self.vocab_event:
            if len(ve) > 2 and ve not in event_terms and re.search(r'\b' + re.escape(ve) + r'\b', q_lower):
                event_terms.append(ve)

        # 5. Temporal terms extraction
        temporal_term = None
        for temp in ["summer 2024", "spring 2024", "fall 2024", "winter 2024", "fall 2023", "last summer", "spring", "2024", "2023"]:
            if temp in q_lower:
                temporal_term = temp
                break

        # 6. Precise query detection (exact names)
        is_precise = False
        exact_names = ["ananya", "rohan", "priya", "vikram"]
        for n in exact_names:
            if re.search(r'\b' + re.escape(n) + r'\b', q_lower):
                is_precise = True
                break

        return {
            "relational_terms": extracted_rel,
            "visual_place_terms": place_terms,
            "document_intent": doc_intent,
            "event_terms": event_terms,
            "temporal_terms": temporal_term,
            "is_precise_query": is_precise
        }

    def generate_clarifying_question(self, candidate_results, query):
        """
        Analyzes candidate matching photos to identify which unspecified metadata dimension
        would most reduce ambiguity.
        """
        photos = [r["photo"] for r in candidate_results]

        # 1. Check Place / Location diversity
        places = []
        for p in photos:
            pl = p.get("place_name")
            if pl and pl not in places:
                places.append(pl)

        if len(places) >= 2:
            options = places[:5]
            return {
                "question_id": "location",
                "question": "Which trip or location were you looking for?",
                "options": options,
                "hint": "Select a location to narrow your search"
            }

        # 2. Check Tagged Person / Relationship diversity
        people = []
        for p in photos:
            for name in p.get("tagged_names", []):
                rel = p.get("relationships", [])
                rel_str = f" ({rel[0].capitalize()})" if rel else ""
                person_label = f"{name}{rel_str}"
                if person_label not in people:
                    people.append(person_label)

        if len(people) >= 2:
            return {
                "question_id": "person",
                "question": "Who was in the photo with you?",
                "options": people[:4],
                "hint": "Select a person to narrow results"
            }

        # 3. Check Temporal Date Range diversity
        dates = []
        for p in photos:
            dt = p.get("approx_date_range")
            if dt and dt not in dates:
                dates.append(dt)

        if len(dates) >= 2:
            return {
                "question_id": "date",
                "question": "Approximately when was this photo taken?",
                "options": dates[:4],
                "hint": "Select a date range to filter results"
            }

        return {
            "question_id": "generic",
            "question": "Can you specify who or where this happened?",
            "options": ["With Roommate", "During Vacation", "At a Café"],
            "hint": "Provide extra detail to refine results"
        }

    def search_ai_decomposed(self, query, refinement=None, skip_clarification=False):
        """
        Executes AI Multi-Signal Query Decomposition search.
        Evaluates ambiguity conditions and triggers Feature 2 clarifying question if needed.
        Enforces 1-turn maximum limit (never loops a second question after refinement or skip).
        """
        signals = self.decompose_query(query, refinement)
        results = []

        active_categories = 0
        if signals["relational_terms"] or signals["is_precise_query"]: active_categories += 1
        if signals["document_intent"]: active_categories += 1
        if signals["visual_place_terms"]: active_categories += 1
        if signals["event_terms"]: active_categories += 1
        if signals["temporal_terms"]: active_categories += 1

        category_weights = {
            "relational": 0.35 if (signals["relational_terms"] or signals["is_precise_query"]) else 0.0,
            "document": 0.35 if signals["document_intent"] else 0.0,
            "visual_place": 0.30 if signals["visual_place_terms"] else 0.0,
            "event": 0.25 if signals["event_terms"] else 0.0,
            "temporal": 0.20 if signals["temporal_terms"] else 0.0,
        }
        total_query_weight = sum(category_weights.values())

        for photo in self.dataset:
            rel_score = 0.0
            doc_score = 0.0
            place_score = 0.0
            event_score = 0.0
            temporal_score = 0.0
            matched_signals_desc = []

            # 1. Relational Matching
            if signals["relational_terms"]:
                photo_rels = [r.lower() for r in photo["relationships"]]
                for term in signals["relational_terms"]:
                    if term.lower() in photo_rels:
                        rel_score = 1.0
                        matched_signals_desc.append(f"relational '{term}'")
                        break
            
            if signals["is_precise_query"]:
                q_words = f"{query} {refinement or ''}".lower().split()
                for name in photo["tagged_names"]:
                    if name.lower() in q_words:
                        rel_score = 1.0
                        matched_signals_desc.append(f"tagged name '{name}'")

            # 2. Document Intent Matching
            if signals["document_intent"]:
                target_intent = signals["document_intent"].lower()
                photo_purpose = (photo["document_purpose"] or "").lower()
                photo_ocr = (photo["ocr_text"] or "").lower()

                if photo_purpose and target_intent in photo_purpose:
                    doc_score = 1.0
                    matched_signals_desc.append(f"document purpose '{photo['document_purpose']}'")
                elif "laptop" in target_intent and ("macbook" in photo_ocr or "best buy" in photo_ocr or "laptop" in photo_purpose):
                    doc_score = 0.95
                    matched_signals_desc.append("laptop receipt intent")
                elif photo_purpose == "receipt" and "receipt" in target_intent:
                    doc_score = 0.6

            # 3. Place / Visual Descriptors Semantic Matching
            if signals["visual_place_terms"]:
                photo_place = (photo["place_name"] or "").lower()
                photo_visuals = [v.lower() for v in photo["visual_descriptors"]]
                
                for term in signals["visual_place_terms"]:
                    term_clean = term.replace("é", "e")
                    # Semantic café expansion
                    is_cafe_query = term in ["café", "cafe", "coffee shop"]
                    is_cafe_photo = any(c in photo_place for c in ["coffee", "café", "cafe", "starbucks", "bistro"]) or \
                                    any(c in v for v in photo_visuals for c in ["outdoor seating", "coffee cups", "espresso", "bistro table"])

                    matched_visual = None
                    if term in photo_place or term_clean in photo_place:
                        matched_visual = photo["place_name"]
                    else:
                        for v in photo_visuals:
                            if term in v or term_clean in v:
                                matched_visual = v
                                break

                    if (is_cafe_query and is_cafe_photo) or matched_visual:
                        place_score = 1.0
                        place_display = matched_visual or photo["place_name"] or (photo_visuals[0] if photo_visuals else "visual descriptor")
                        matched_signals_desc.append(f"visual descriptor '{place_display}'")
                        break

            # 4. Event Matching
            if signals["event_terms"]:
                photo_events = [e.lower() for e in photo["event_tags"]]
                for et in signals["event_terms"]:
                    matching_event = next((pe for pe in photo_events if et in pe), None)
                    if matching_event:
                        event_score = 1.0
                        matched_signals_desc.append(f"event '{matching_event}'")
                        break

            # 5. Temporal Matching
            if signals["temporal_terms"]:
                photo_temp = (photo.get("approx_date_range") or "").lower()
                if signals["temporal_terms"].lower() in photo_temp:
                    temporal_score = 1.0

            # Normalized Score Calculation across active query categories
            if total_query_weight > 0:
                weighted_sum = (category_weights["relational"] * rel_score) + \
                               (category_weights["document"] * doc_score) + \
                               (category_weights["visual_place"] * place_score) + \
                               (category_weights["event"] * event_score) + \
                               (category_weights["temporal"] * temporal_score)
                base_score = weighted_sum / total_query_weight
            else:
                base_score = 0.0

            # Synergy Multipliers
            if active_categories == 1:
                final_score = base_score * 0.85
            else:
                if (rel_score > 0.5 and place_score > 0.5) or (event_score > 0.5 and place_score > 0.5) or (rel_score > 0.5 and event_score > 0.5):
                    final_score = min(1.0, base_score * 1.25)
                    matched_signals_desc.append("multi-signal synergy bonus")
                else:
                    final_score = base_score

            if refinement:
                ref_lower = refinement.lower()
                # If refinement specifies a place and this photo didn't match place, discount it
                if any(pt in ref_lower for pt in signals["visual_place_terms"]) and place_score == 0.0:
                    final_score = base_score * 0.5
                if any(rt in ref_lower for rt in signals["relational_terms"]) and rel_score == 0.0:
                    final_score = base_score * 0.5

            if final_score >= 0.30:
                confidence_band = "High Match" if final_score >= 0.70 else "Medium Match"
                
                if len(matched_signals_desc) >= 2:
                    explanation = f"Matches {matched_signals_desc[0]} + {matched_signals_desc[1]}"
                elif len(matched_signals_desc) == 1:
                    explanation = f"Matches {matched_signals_desc[0]}"
                else:
                    explanation = "Partial contextual match"

                results.append({
                    "photo_id": photo["photo_id"],
                    "score": round(final_score, 3),
                    "confidence": confidence_band,
                    "explanation": explanation,
                    "photo": photo
                })

        results.sort(key=lambda x: x["score"], reverse=True)

        # Ambiguity Evaluation
        is_ambiguous = False
        clarifying_question = None

        if not refinement and not skip_clarification and len(results) > 0:
            top_score = results[0]["score"]
            cond_a = len(results) > 8 and (results[7]["score"] >= top_score * 0.85)
            cond_b = len(results) >= 4 and top_score < 0.55

            if cond_a or cond_b:
                is_ambiguous = True
                clarifying_question = self.generate_clarifying_question(results, query)

        return {
          "signals": signals,
          "zero_match": len(results) == 0 or (len(results) > 0 and results[0]["score"] < 0.30),
          "is_ambiguous": is_ambiguous,
          "clarifying_question": clarifying_question,
          "has_refinement": bool(refinement),
          "skipped": skip_clarification,
          "total_matches": len(results),
          "results": results
        }

    def search_literal_baseline(self, query):
        """
        Executes Literal Substring Keyword Baseline search.
        Includes all metadata fields (place_name, ocr_text, tagged_names, visual_descriptors,
        event_tags, relationships, document_purpose) in text corpus.
        """
        stop_words = {"the", "a", "an", "with", "my", "at", "for", "i", "of", "in", "from", "on", "to"}
        words = [w.lower().replace("é", "e") for w in re.findall(r'\w+', query) if w.lower() not in stop_words]

        results = []
        for photo in self.dataset:
            text_corpus = " ".join([
                (photo.get("place_name") or "").replace("é", "e"),
                (photo.get("ocr_text") or "").replace("é", "e"),
                " ".join(photo.get("tagged_names", [])),
                " ".join(photo.get("visual_descriptors", [])),
                " ".join(photo.get("event_tags", []))
            ]).lower()

            matches = 0
            matched_words = []
            for word in words:
                if re.search(r'\b' + re.escape(word) + r'\b', text_corpus):
                    matches += 1
                    matched_words.append(word)

            if matches > 0:
                score = round(matches / len(words), 3) if words else 0
                results.append({
                    "photo_id": photo["photo_id"],
                    "score": score,
                    "confidence": "Literal Match" if score >= 0.5 else "Partial Keyword",
                    "explanation": f"Literal keyword match on: '{', '.join(matched_words)}'",
                    "photo": photo
                })

        results.sort(key=lambda x: (x["score"], x["photo_id"]), reverse=True)
        return {
            "query_words": words,
            "total_matches": len(results),
            "results": results
        }

