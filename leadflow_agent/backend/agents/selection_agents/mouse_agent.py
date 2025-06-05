from backend.utils.db_queries import run_query

def MouseAgent(state: dict) -> dict:
    goals = state.get("user_goals", {})
    budget = goals.get("budget", 1000)
    mouse_priority = goals.get("mouse_priority", "medium")
    
    mouse_weight_map = {"low": 0.02, "medium": 0.03, "high": 0.05}
    max_mouse_price = budget * mouse_weight_map.get(mouse_priority, 0.03)
    
    # Build filter conditions
    filters = ["price <= %s"]
    params = [max_mouse_price]
    
    # Tracking method preference
    if "tracking_method" in goals:
        filters.append("tracking_method = %s")
        params.append(goals["tracking_method"])
    
    # Connection type preference
    if "connection_type" in goals:
        filters.append("connection_type = %s")
        params.append(goals["connection_type"])
    
    # DPI requirements
    if "min_dpi" in goals:
        filters.append("max_dpi >= %s")
        params.append(goals["min_dpi"])
    
    # Hand orientation preference
    if "hand_orientation" in goals:
        filters.append("hand_orientation = %s")
        params.append(goals["hand_orientation"])
    
    # Color preference
    if "mouse_color" in goals:
        filters.append("color = %s")
        params.append(goals["mouse_color"])
    
    # Preferred brand
    brands = goals.get("preferred_mouse_brands", [])
    if brands:
        brand_conditions = " OR ".join(["name ILIKE %s" for _ in brands])
        filters.append(f"({brand_conditions})")
        params.extend([f"%{brand}%" for brand in brands])
    
    filter_sql = " AND ".join(filters)
    
    query = f"""
    SELECT * FROM mouse
    WHERE {filter_sql}
    ORDER BY 
        max_dpi DESC,
        CASE 
            WHEN connection_type = 'Wireless' THEN 1
            ELSE 2
        END,
        price ASC
    LIMIT 1
    """
    
    results = run_query(query, params)
    
    if results:
        mouse = results[0]
        state["selected_parts"]["mouse"] = mouse
        state["current_total_cost"] += mouse["price"]
        state["part_attempt_log"]["mouse"].append(mouse["name"])
    else:
        state["compatibility_issues"].append("No compatible mouse found.")
        state["budget_violation"] = True

    return state 