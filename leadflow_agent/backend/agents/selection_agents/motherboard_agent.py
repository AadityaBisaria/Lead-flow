from backend.utils.db_queries import run_query

def MotherboardAgent(state: dict) -> dict:
    goals = state.get("user_goals", {})
    budget = goals.get("budget", 1000)
    mb_priority = goals.get("motherboard_priority", "medium")
    
    mb_weight_map = {"low": 0.15, "medium": 0.2, "high": 0.25}
    max_mb_price = budget * mb_weight_map.get(mb_priority, 0.2)
    
    # Build filter conditions
    filters = ["price <= %s"]
    params = [max_mb_price]
    
    # CPU Socket compatibility
    if "selected_parts" in state and "cpu" in state["selected_parts"]:
        cpu = state["selected_parts"]["cpu"]
        filters.append("socket = %s")
        params.append(cpu["socket"])
    
    # Form factor compatibility with case
    if "selected_parts" in state and "case" in state["selected_parts"]:
        case = state["selected_parts"]["case"]
        filters.append("form_factor = %s")
        params.append(case["form_factor"])
    
    # Memory requirements
    if "min_memory" in goals:
        filters.append("max_memory >= %s")
        params.append(goals["min_memory"])
    
    if "min_memory_slots" in goals:
        filters.append("memory_slots >= %s")
        params.append(goals["min_memory_slots"])
    
    # Color preference
    if "motherboard_color" in goals:
        filters.append("color = %s")
        params.append(goals["motherboard_color"])
    
    # Preferred brand
    brands = goals.get("preferred_motherboard_brands", [])
    if brands:
        brand_conditions = " OR ".join(["name ILIKE %s" for _ in brands])
        filters.append(f"({brand_conditions})")
        params.extend([f"%{brand}%" for brand in brands])
    
    filter_sql = " AND ".join(filters)
    
    query = f"""
    SELECT * FROM motherboard
    WHERE {filter_sql}
    ORDER BY 
        max_memory DESC,
        memory_slots DESC,
        price ASC
    LIMIT 1
    """
    
    results = run_query(query, params)
    
    if results:
        motherboard = results[0]
        state["selected_parts"]["motherboard"] = motherboard
        state["current_total_cost"] += motherboard["price"]
        state["part_attempt_log"]["motherboard"].append(motherboard["name"])
    else:
        state["compatibility_issues"].append("No compatible motherboard found.")
        state["budget_violation"] = True

    return state 