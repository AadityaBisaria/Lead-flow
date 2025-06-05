from backend.utils.db_queries import run_query

def ThermalPasteAgent(state: dict) -> dict:
    goals = state.get("user_goals", {})
    budget = goals.get("budget", 1000)
    paste_priority = goals.get("paste_priority", "medium")
    
    paste_weight_map = {"low": 0.005, "medium": 0.01, "high": 0.015}
    max_paste_price = budget * paste_weight_map.get(paste_priority, 0.01)
    
    # Build filter conditions
    filters = ["price <= %s"]
    params = [max_paste_price]
    
    # Amount requirements
    if "min_amount" in goals:
        filters.append("amount >= %s")
        params.append(goals["min_amount"])
    
    # Preferred brand
    brands = goals.get("preferred_paste_brands", [])
    if brands:
        brand_conditions = " OR ".join(["name ILIKE %s" for _ in brands])
        filters.append(f"({brand_conditions})")
        params.extend([f"%{brand}%" for brand in brands])
    
    filter_sql = " AND ".join(filters)
    
    query = f"""
    SELECT * FROM thermal_paste
    WHERE {filter_sql}
    ORDER BY 
        amount DESC,
        price ASC
    LIMIT 1
    """
    
    results = run_query(query, params)
    
    if results:
        paste = results[0]
        state["selected_parts"]["thermal_paste"] = paste
        state["current_total_cost"] += paste["price"]
        state["part_attempt_log"]["thermal_paste"].append(paste["name"])
    else:
        state["compatibility_issues"].append("No compatible thermal paste found.")
        state["budget_violation"] = True

    return state 