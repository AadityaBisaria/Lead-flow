from backend.utils.db_queries import run_query

def SpeakersAgent(state: dict) -> dict:
    goals = state.get("user_goals", {})
    budget = goals.get("budget", 1000)
    speakers_priority = goals.get("speakers_priority", "medium")
    
    speakers_weight_map = {"low": 0.02, "medium": 0.03, "high": 0.05}
    max_speakers_price = budget * speakers_weight_map.get(speakers_priority, 0.03)
    
    # Build filter conditions
    filters = ["price <= %s"]
    params = [max_speakers_price]
    
    # Configuration requirements
    if "min_configuration" in goals:
        filters.append("configuration >= %s")
        params.append(goals["min_configuration"])
    
    # Wattage requirements
    if "min_wattage" in goals:
        filters.append("wattage >= %s")
        params.append(goals["min_wattage"])
    
    # Frequency response requirements
    if "min_frequency" in goals:
        filters.append("%s >= ANY(frequency_response)")
        params.append(goals["min_frequency"])
    
    if "max_frequency" in goals:
        filters.append("%s <= ANY(frequency_response)")
        params.append(goals["max_frequency"])
    
    # Color preference
    if "speaker_color" in goals:
        filters.append("color = %s")
        params.append(goals["speaker_color"])
    
    # Preferred brand
    brands = goals.get("preferred_speaker_brands", [])
    if brands:
        brand_conditions = " OR ".join(["name ILIKE %s" for _ in brands])
        filters.append(f"({brand_conditions})")
        params.extend([f"%{brand}%" for brand in brands])
    
    filter_sql = " AND ".join(filters)
    
    query = f"""
    SELECT * FROM speakers
    WHERE {filter_sql}
    ORDER BY 
        configuration DESC,
        wattage DESC,
        price ASC
    LIMIT 1
    """
    
    results = run_query(query, params)
    
    if results:
        speakers = results[0]
        state["selected_parts"]["speakers"] = speakers
        state["current_total_cost"] += speakers["price"]
        state["part_attempt_log"]["speakers"].append(speakers["name"])
    else:
        state["compatibility_issues"].append("No compatible speakers found.")
        state["budget_violation"] = True

    return state 