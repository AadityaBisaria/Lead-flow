from backend.utils.db_queries import run_query

def CPUCoolerAgent(state: dict) -> dict:
    goals = state.get("user_goals", {})
    budget = goals.get("budget", 1000)
    cooler_priority = goals.get("cooler_priority", "medium")
    
    cooler_weight_map = {"low": 0.05, "medium": 0.1, "high": 0.15}
    max_cooler_price = budget * cooler_weight_map.get(cooler_priority, 0.1)
    
    # Build filter conditions
    filters = ["price <= %s"]
    params = [max_cooler_price]
    
    # Size compatibility
    if "selected_parts" in state and "case" in state["selected_parts"]:
        case = state["selected_parts"]["case"]
        if "max_cooler_height" in case:
            filters.append("size <= %s")
            params.append(case["max_cooler_height"])
    
    # Color preference
    if "cooler_color" in goals:
        filters.append("color = %s")
        params.append(goals["cooler_color"])
    
    # Noise level preference
    if "max_noise_level" in goals:
        filters.append("noise_level[1] <= %s")  # Using first element of noise_level array
        params.append(goals["max_noise_level"])
    
    # RPM preference
    if "min_rpm" in goals:
        filters.append("rpm[1] >= %s")  # Using first element of rpm array
        params.append(goals["min_rpm"])
    
    # Preferred brand
    brands = goals.get("preferred_cooler_brands", [])
    if brands:
        brand_conditions = " OR ".join(["name ILIKE %s" for _ in brands])
        filters.append(f"({brand_conditions})")
        params.extend([f"%{brand}%" for brand in brands])
    
    filter_sql = " AND ".join(filters)
    
    query = f"""
    SELECT * FROM cpu_cooler
    WHERE {filter_sql}
    ORDER BY 
        rpm[1] DESC,
        noise_level[1] ASC,
        size DESC,
        price ASC
    LIMIT 1
    """
    
    results = run_query(query, params)
    
    if results:
        cooler = results[0]
        state["selected_parts"]["cpu_cooler"] = cooler
        state["current_total_cost"] += cooler["price"]
        state["part_attempt_log"]["cpu_cooler"].append(cooler["name"])
    else:
        state["compatibility_issues"].append("No compatible CPU cooler found.")
        state["budget_violation"] = True

    return state 