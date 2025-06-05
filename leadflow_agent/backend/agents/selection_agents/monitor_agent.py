from backend.utils.db_queries import run_query

def MonitorAgent(state: dict) -> dict:
    goals = state.get("user_goals", {})
    budget = goals.get("budget", 1000)
    monitor_priority = goals.get("monitor_priority", "medium")
    
    monitor_weight_map = {"low": 0.1, "medium": 0.15, "high": 0.2}
    max_monitor_price = budget * monitor_weight_map.get(monitor_priority, 0.15)
    
    # Build filter conditions
    filters = ["price <= %s"]
    params = [max_monitor_price]
    
    # Screen size requirements
    if "min_screen_size" in goals:
        filters.append("screen_size >= %s")
        params.append(goals["min_screen_size"])
    
    # Resolution requirements
    if "min_resolution" in goals:
        filters.append("resolution && ARRAY[%s]")
        params.append(goals["min_resolution"])
    
    # Refresh rate requirements
    if "min_refresh_rate" in goals:
        filters.append("refresh_rate >= %s")
        params.append(goals["min_refresh_rate"])
    
    # Response time requirements
    if "max_response_time" in goals:
        filters.append("response_time <= %s")
        params.append(goals["max_response_time"])
    
    # Panel type preference
    if "panel_type" in goals:
        filters.append("panel_type = %s")
        params.append(goals["panel_type"])
    
    # Aspect ratio preference
    if "aspect_ratio" in goals:
        filters.append("aspect_ratio = %s")
        params.append(goals["aspect_ratio"])
    
    # Preferred brand
    brands = goals.get("preferred_monitor_brands", [])
    if brands:
        brand_conditions = " OR ".join(["name ILIKE %s" for _ in brands])
        filters.append(f"({brand_conditions})")
        params.extend([f"%{brand}%" for brand in brands])
    
    filter_sql = " AND ".join(filters)
    
    query = f"""
    SELECT * FROM monitor
    WHERE {filter_sql}
    ORDER BY 
        resolution[1] DESC,
        refresh_rate DESC,
        response_time ASC,
        screen_size DESC,
        price ASC
    LIMIT 1
    """
    
    results = run_query(query, params)
    
    if results:
        monitor = results[0]
        state["selected_parts"]["monitor"] = monitor
        state["current_total_cost"] += monitor["price"]
        state["part_attempt_log"]["monitor"].append(monitor["name"])
    else:
        state["compatibility_issues"].append("No compatible monitor found.")
        state["budget_violation"] = True

    return state 