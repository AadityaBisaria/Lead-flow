from backend.utils.db_queries import run_query

def PowerSupplyAgent(state: dict) -> dict:
    goals = state.get("user_goals", {})
    budget = goals.get("budget", 1000)
    psu_priority = goals.get("psu_priority", "medium")
    
    psu_weight_map = {"low": 0.1, "medium": 0.15, "high": 0.2}
    max_psu_price = budget * psu_weight_map.get(psu_priority, 0.15)
    
    # Calculate required wattage based on selected components
    required_wattage = 0
    if "selected_parts" in state:
        parts = state["selected_parts"]
        if "cpu" in parts:
            required_wattage += parts["cpu"].get("tdp", 0)
        if "video_card" in parts:
            required_wattage += parts["video_card"].get("power_consumption", 0)
        # Add base system power (motherboard, memory, etc.)
        required_wattage += 100
    
    # Add 20% buffer for safety
    required_wattage = int(required_wattage * 1.2)
    
    # Build filter conditions
    filters = ["price <= %s", "wattage >= %s"]
    params = [max_psu_price, required_wattage]
    
    # Type preference
    if "psu_type" in goals:
        filters.append("type = %s")
        params.append(goals["psu_type"])
    
    # Efficiency rating if specified
    if "efficiency_rating" in goals:
        filters.append("efficiency = %s")
        params.append(goals["efficiency_rating"])
    
    # Modular preference
    if "modular_preference" in goals:
        filters.append("modular->>'type' = %s")
        params.append(goals["modular_preference"])
    
    # Color preference
    if "psu_color" in goals:
        filters.append("color = %s")
        params.append(goals["psu_color"])
    
    # Preferred brand
    brands = goals.get("preferred_psu_brands", [])
    if brands:
        brand_conditions = " OR ".join(["name ILIKE %s" for _ in brands])
        filters.append(f"({brand_conditions})")
        params.extend([f"%{brand}%" for brand in brands])
    
    filter_sql = " AND ".join(filters)
    
    query = f"""
    SELECT * FROM power_supply
    WHERE {filter_sql}
    ORDER BY 
        efficiency DESC,
        wattage ASC,
        price ASC
    LIMIT 1
    """
    
    results = run_query(query, params)
    
    if results:
        psu = results[0]
        state["selected_parts"]["power_supply"] = psu
        state["current_total_cost"] += psu["price"]
        state["part_attempt_log"]["power_supply"].append(psu["name"])
    else:
        state["compatibility_issues"].append("No compatible power supply found.")
        state["budget_violation"] = True

    return state 