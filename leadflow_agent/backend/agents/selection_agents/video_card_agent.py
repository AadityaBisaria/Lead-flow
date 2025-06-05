from backend.utils.db_queries import run_query

def VideoCardAgent(state: dict) -> dict:
    goals = state.get("user_goals", {})
    budget = goals.get("budget", 1000)
    gpu_priority = goals.get("gpu_priority", "medium")
    
    gpu_weight_map = {"low": 0.2, "medium": 0.3, "high": 0.4}
    max_gpu_price = budget * gpu_weight_map.get(gpu_priority, 0.3)
    
    # Build filter conditions
    filters = ["price <= %s"]
    params = [max_gpu_price]
    
    # Chipset preference
    if "chipset_preference" in goals:
        filters.append("chipset = %s")
        params.append(goals["chipset_preference"])
    
    # Minimum VRAM requirement
    if "min_vram" in goals:
        filters.append("memory >= %s")
        params.append(goals["min_vram"])
    
    # Minimum core clock requirement
    if "gpu_min_core_clock" in goals:
        filters.append("core_clock >= %s")
        params.append(goals["gpu_min_core_clock"])
    
    # Minimum boost clock requirement
    if "gpu_min_boost_clock" in goals:
        filters.append("boost_clock >= %s")
        params.append(goals["gpu_min_boost_clock"])
    
    # Color preference
    if "gpu_color" in goals:
        filters.append("color = %s")
        params.append(goals["gpu_color"])
    
    # Case compatibility
    if "selected_parts" in state and "case" in state["selected_parts"]:
        case = state["selected_parts"]["case"]
        filters.append("length <= %s")
        params.append(case["max_gpu_length"])
    
    # Preferred brand
    brands = goals.get("preferred_gpu_brands", [])
    if brands:
        brand_conditions = " OR ".join(["name ILIKE %s" for _ in brands])
        filters.append(f"({brand_conditions})")
        params.extend([f"%{brand}%" for brand in brands])
    
    filter_sql = " AND ".join(filters)
    
    query = f"""
    SELECT * FROM video_card
    WHERE {filter_sql}
    ORDER BY 
        boost_clock DESC,
        core_clock DESC,
        memory DESC,
        price ASC
    LIMIT 1
    """
    
    results = run_query(query, params)
    
    if results:
        gpu = results[0]
        state["selected_parts"]["video_card"] = gpu
        state["current_total_cost"] += gpu["price"]
        state["part_attempt_log"]["video_card"].append(gpu["name"])
    else:
        state["compatibility_issues"].append("No compatible video card found.")
        state["budget_violation"] = True

    return state 