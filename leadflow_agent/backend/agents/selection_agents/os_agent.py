from backend.utils.db_queries import run_query

def OperatingSystemAgent(state: dict) -> dict:
    goals = state.get("user_goals", {})
    budget = goals.get("budget", 1000)
    os_priority = goals.get("os_priority", "medium")
    
    os_weight_map = {"low": 0.05, "medium": 0.1, "high": 0.15}
    max_os_price = budget * os_weight_map.get(os_priority, 0.1)
    
    # Build filter conditions
    filters = ["price <= %s"]
    params = [max_os_price]
    
    # Mode preference (32-bit/64-bit)
    if "os_mode" in goals:
        filters.append("%s = ANY(mode)")
        params.append(goals["os_mode"])
    
    # Memory compatibility
    if "selected_parts" in state and "memory" in state["selected_parts"]:
        memory = state["selected_parts"]["memory"]
        total_memory = memory["capacity"] * len(state["selected_parts"].get("memory", []))
        filters.append("max_memory >= %s")
        params.append(total_memory)
    
    # Preferred brand
    brands = goals.get("preferred_os_brands", [])
    if brands:
        brand_conditions = " OR ".join(["name ILIKE %s" for _ in brands])
        filters.append(f"({brand_conditions})")
        params.extend([f"%{brand}%" for brand in brands])
    
    filter_sql = " AND ".join(filters)
    
    query = f"""
    SELECT * FROM os
    WHERE {filter_sql}
    ORDER BY 
        max_memory DESC,
        price ASC
    LIMIT 1
    """
    
    results = run_query(query, params)
    
    if results:
        os = results[0]
        state["selected_parts"]["operating_system"] = os
        state["current_total_cost"] += os["price"]
        state["part_attempt_log"]["operating_system"].append(os["name"])
    else:
        state["compatibility_issues"].append("No compatible operating system found.")
        state["budget_violation"] = True

    return state 