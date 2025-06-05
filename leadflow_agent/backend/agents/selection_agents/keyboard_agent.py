from backend.utils.db_queries import run_query

def KeyboardAgent(state: dict) -> dict:
    goals = state.get("user_goals", {})
    budget = goals.get("budget", 1000)
    keyboard_priority = goals.get("keyboard_priority", "medium")
    
    keyboard_weight_map = {"low": 0.02, "medium": 0.03, "high": 0.05}
    max_keyboard_price = budget * keyboard_weight_map.get(keyboard_priority, 0.03)
    
    # Build filter conditions
    filters = ["price <= %s"]
    params = [max_keyboard_price]
    
    # Style preference
    if "keyboard_style" in goals:
        filters.append("style = %s")
        params.append(goals["keyboard_style"])
    
    # Switch type preference
    if "switch_type" in goals:
        filters.append("switches = %s")
        params.append(goals["switch_type"])
    
    # Backlight preference
    if "backlight_type" in goals:
        filters.append("backlit = %s")
        params.append(goals["backlight_type"])
    
    # Tenkeyless preference
    if "require_tenkeyless" in goals:
        filters.append("tenkeyless = %s")
        params.append(goals["require_tenkeyless"])
    
    # Connection type preference
    if "connection_type" in goals:
        filters.append("connection_type = %s")
        params.append(goals["connection_type"])
    
    # Color preference
    if "keyboard_color" in goals:
        filters.append("color = %s")
        params.append(goals["keyboard_color"])
    
    # Preferred brand
    brands = goals.get("preferred_keyboard_brands", [])
    if brands:
        brand_conditions = " OR ".join(["name ILIKE %s" for _ in brands])
        filters.append(f"({brand_conditions})")
        params.extend([f"%{brand}%" for brand in brands])
    
    filter_sql = " AND ".join(filters)
    
    query = f"""
    SELECT * FROM keyboard
    WHERE {filter_sql}
    ORDER BY 
        CASE 
            WHEN style = 'Mechanical' THEN 1
            ELSE 2
        END,
        CASE 
            WHEN backlit = 'RGB' THEN 1
            WHEN backlit = 'Yes' THEN 2
            ELSE 3
        END,
        price ASC
    LIMIT 1
    """
    
    results = run_query(query, params)
    
    if results:
        keyboard = results[0]
        state["selected_parts"]["keyboard"] = keyboard
        state["current_total_cost"] += keyboard["price"]
        state["part_attempt_log"]["keyboard"].append(keyboard["name"])
    else:
        state["compatibility_issues"].append("No compatible keyboard found.")
        state["budget_violation"] = True

    return state 