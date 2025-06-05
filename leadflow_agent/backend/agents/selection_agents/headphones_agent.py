from backend.utils.db_queries import run_query

def HeadphonesAgent(state: dict) -> dict:
    goals = state.get("user_goals", {})
    budget = goals.get("budget", 1000)
    headphones_priority = goals.get("headphones_priority", "medium")
    
    headphones_weight_map = {"low": 0.02, "medium": 0.03, "high": 0.05}
    max_headphones_price = budget * headphones_weight_map.get(headphones_priority, 0.03)
    
    # Build filter conditions
    filters = ["price <= %s"]
    params = [max_headphones_price]
    
    # Headphone type
    if "headphone_type" in goals:
        filters.append("type = %s")
        params.append(goals["headphone_type"])
    
    # Frequency response requirements
    if "min_frequency" in goals and "max_frequency" in goals:
        filters.append("frequency_response && ARRAY[%s, %s]")
        params.extend([goals["min_frequency"], goals["max_frequency"]])
    
    # Microphone requirement
    if goals.get("require_microphone"):
        filters.append("microphone = TRUE")
    
    # Wireless requirement
    if goals.get("require_wireless"):
        filters.append("wireless = TRUE")
    
    # Enclosure type preference
    if "enclosure_type" in goals:
        filters.append("enclosure_type = %s")
        params.append(goals["enclosure_type"])
    
    # Color preference
    if "headphone_color" in goals:
        filters.append("color = %s")
        params.append(goals["headphone_color"])
    
    # Preferred brand
    brands = goals.get("preferred_headphone_brands", [])
    if brands:
        brand_conditions = " OR ".join(["name ILIKE %s" for _ in brands])
        filters.append(f"({brand_conditions})")
        params.extend([f"%{brand}%" for brand in brands])
    
    filter_sql = " AND ".join(filters)
    
    query = f"""
    SELECT * FROM headphones
    WHERE {filter_sql}
    ORDER BY 
        CASE 
            WHEN wireless = TRUE THEN 1
            ELSE 2
        END,
        CASE 
            WHEN microphone = TRUE THEN 1
            ELSE 2
        END,
        price ASC
    LIMIT 1
    """
    
    results = run_query(query, params)
    
    if results:
        headphones = results[0]
        state["selected_parts"]["headphones"] = headphones
        state["current_total_cost"] += headphones["price"]
        state["part_attempt_log"]["headphones"].append(headphones["name"])
    else:
        state["compatibility_issues"].append("No compatible headphones found.")
        state["budget_violation"] = True

    return state 