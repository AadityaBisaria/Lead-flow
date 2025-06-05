from backend.utils.db_queries import run_query

def CaseAccessoryAgent(state: dict) -> dict:
    goals = state.get("user_goals", {})
    budget = goals.get("budget", 1000)
    accessory_priority = goals.get("accessory_priority", "medium")
    
    accessory_weight_map = {"low": 0.02, "medium": 0.03, "high": 0.05}
    max_accessory_price = budget * accessory_weight_map.get(accessory_priority, 0.03)
    
    # Build filter conditions
    filters = ["price <= %s"]
    params = [max_accessory_price]
    
    # Accessory type preference
    if "accessory_type" in goals:
        filters.append("type = %s")
        params.append(goals["accessory_type"])
    
    # Form factor compatibility check
    if "selected_parts" in state and "case" in state["selected_parts"]:
        case = state["selected_parts"]["case"]
        if "type" in case:
            filters.append("form_factor <= %s")
            params.append(case["type"])
    
    # Preferred brand
    brands = goals.get("preferred_accessory_brands", [])
    if brands:
        brand_conditions = " OR ".join(["name ILIKE %s" for _ in brands])
        filters.append(f"({brand_conditions})")
        params.extend([f"%{brand}%" for brand in brands])
    
    filter_sql = " AND ".join(filters)
    
    query = f"""
    SELECT * FROM case_accessory
    WHERE {filter_sql}
    ORDER BY 
        form_factor DESC,
        price ASC
    LIMIT 1
    """
    
    results = run_query(query, params)
    
    if results:
        accessory = results[0]
        state["selected_parts"]["case_accessory"] = accessory
        state["current_total_cost"] += accessory["price"]
        state["part_attempt_log"]["case_accessory"].append(accessory["name"])
    else:
        state["compatibility_issues"].append("No compatible case accessory found.")
        state["budget_violation"] = True

    return state 