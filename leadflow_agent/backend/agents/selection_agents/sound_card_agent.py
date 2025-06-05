from backend.utils.db_queries import run_query

def SoundCardAgent(state: dict) -> dict:
    goals = state.get("user_goals", {})
    budget = goals.get("budget", 1000)
    sound_priority = goals.get("sound_priority", "medium")
    
    sound_weight_map = {"low": 0.02, "medium": 0.03, "high": 0.05}
    max_sound_price = budget * sound_weight_map.get(sound_priority, 0.03)
    
    # Build filter conditions
    filters = ["price <= %s"]
    params = [max_sound_price]
    
    # Interface compatibility with motherboard
    if "selected_parts" in state and "motherboard" in state["selected_parts"]:
        motherboard = state["selected_parts"]["motherboard"]
        filters.append("interface IN (SELECT unnest(%s))")
        params.append(motherboard["expansion_slots"])
    
    # Channel requirements
    if "min_channels" in goals:
        filters.append("channels >= %s")
        params.append(goals["min_channels"])
    
    # Digital audio requirements
    if "min_digital_audio" in goals:
        filters.append("digital_audio >= %s")
        params.append(goals["min_digital_audio"])
    
    # SNR requirements
    if "min_snr" in goals:
        filters.append("snr >= %s")
        params.append(goals["min_snr"])
    
    # Sample rate requirements
    if "min_sample_rate" in goals:
        filters.append("sample_rate >= %s")
        params.append(goals["min_sample_rate"])
    
    # Chipset preference
    if "chipset_preference" in goals:
        filters.append("chipset = %s")
        params.append(goals["chipset_preference"])
    
    # Preferred brand
    brands = goals.get("preferred_sound_brands", [])
    if brands:
        brand_conditions = " OR ".join(["name ILIKE %s" for _ in brands])
        filters.append(f"({brand_conditions})")
        params.extend([f"%{brand}%" for brand in brands])
    
    filter_sql = " AND ".join(filters)
    
    query = f"""
    SELECT * FROM sound_card
    WHERE {filter_sql}
    ORDER BY 
        channels DESC,
        digital_audio DESC,
        snr DESC,
        sample_rate DESC,
        price ASC
    LIMIT 1
    """
    
    results = run_query(query, params)
    
    if results:
        sound_card = results[0]
        state["selected_parts"]["sound_card"] = sound_card
        state["current_total_cost"] += sound_card["price"]
        state["part_attempt_log"]["sound_card"].append(sound_card["name"])
    else:
        state["compatibility_issues"].append("No compatible sound card found.")
        state["budget_violation"] = True

    return state 