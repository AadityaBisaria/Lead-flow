from backend.utils.db_queries import run_query

def CaseAgent(state: dict) -> dict:
    goals = state.get("user_goals", {})
    budget = goals.get("budget", 1000)
    case_priority = goals.get("case_priority", "medium")
    
    case_weight_map = {"low": 0.05, "medium": 0.1, "high": 0.15}
    max_case_price = budget * case_weight_map.get(case_priority, 0.1)
    
    # Build filter conditions
    filters = ["price <= %s"]
    params = [max_case_price]
    
    # Case type preference
    if "case_type" in goals:
        filters.append("type = %s")
        params.append(goals["case_type"])
    
    # Color preference
    if "case_color" in goals:
        filters.append("color = %s")
        params.append(goals["case_color"])
    
    # Side panel preference
    if "side_panel" in goals:
        filters.append("side_panel = %s")
        params.append(goals["side_panel"])
    
    # PSU compatibility check
    if "selected_parts" in state and "power_supply" in state["selected_parts"]:
        psu = state["selected_parts"]["power_supply"]
        if "length" in psu:
            filters.append("psu >= %s")
            params.append(psu["length"])
    
    # Storage bays requirements
    if "min_external_bays" in goals:
        filters.append("external_525_bays >= %s")
        params.append(goals["min_external_bays"])
    
    if "min_internal_bays" in goals:
        filters.append("internal_35_bays >= %s")
        params.append(goals["min_internal_bays"])
    
    # Preferred brand
    brands = goals.get("preferred_case_brands", [])
    if brands:
        brand_conditions = " OR ".join(["name ILIKE %s" for _ in brands])
        filters.append(f"({brand_conditions})")
        params.extend([f"%{brand}%" for brand in brands])
    
    filter_sql = " AND ".join(filters)
    
    query = f"""
    SELECT * FROM case
    WHERE {filter_sql}
    ORDER BY 
        external_525_bays DESC,
        internal_35_bays DESC,
        price ASC
    LIMIT 1
    """
    
    results = run_query(query, params)
    
    if results:
        case = results[0]
        state["selected_parts"]["case"] = case
        state["current_total_cost"] += case["price"]
        state["part_attempt_log"]["case"].append(case["name"])
    else:
        state["compatibility_issues"].append("No compatible case found.")
        state["budget_violation"] = True

    return state 