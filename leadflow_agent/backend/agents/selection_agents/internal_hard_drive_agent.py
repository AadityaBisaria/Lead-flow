from backend.utils.db_queries import run_query

def InternalHardDriveAgent(state: dict) -> dict:
    goals = state.get("user_goals", {})
    budget = goals.get("budget", 1000)
    drive_priority = goals.get("drive_priority", "medium")
    
    drive_weight_map = {"low": 0.1, "medium": 0.15, "high": 0.2}
    max_drive_price = budget * drive_weight_map.get(drive_priority, 0.15)
    
    # Build filter conditions
    filters = ["price <= %s"]
    params = [max_drive_price]
    
    # Capacity requirements
    if "min_capacity" in goals:
        filters.append("capacity >= %s")
        params.append(goals["min_capacity"])
    
    # Drive type preference
    if "drive_type" in goals:
        filters.append("type->>'type' = %s")
        params.append(goals["drive_type"])
    
    # Cache requirements
    if "min_cache" in goals:
        filters.append("cache >= %s")
        params.append(goals["min_cache"])
    
    # Form factor compatibility with case
    if "selected_parts" in state and "case" in state["selected_parts"]:
        case = state["selected_parts"]["case"]
        filters.append("form_factor ? %s")
        params.append(case["drive_bays"])
    
    # Interface compatibility with motherboard
    if "selected_parts" in state and "motherboard" in state["selected_parts"]:
        motherboard = state["selected_parts"]["motherboard"]
        filters.append("interface IN (SELECT unnest(%s))")
        params.append(motherboard["storage_interfaces"])
    
    # Preferred brand
    brands = goals.get("preferred_drive_brands", [])
    if brands:
        brand_conditions = " OR ".join(["name ILIKE %s" for _ in brands])
        filters.append(f"({brand_conditions})")
        params.extend([f"%{brand}%" for brand in brands])
    
    filter_sql = " AND ".join(filters)
    
    query = f"""
    SELECT * FROM internal_hard_drive
    WHERE {filter_sql}
    ORDER BY 
        CASE 
            WHEN type->>'type' = 'SSD' THEN 1
            WHEN type->>'type' = 'HDD' THEN 2
            ELSE 3
        END,
        capacity DESC,
        price_per_gb ASC,
        price ASC
    LIMIT 1
    """
    
    results = run_query(query, params)
    
    if results:
        drive = results[0]
        state["selected_parts"]["internal_hard_drive"] = drive
        state["current_total_cost"] += drive["price"]
        state["part_attempt_log"]["internal_hard_drive"].append(drive["name"])
    else:
        state["compatibility_issues"].append("No compatible internal hard drive found.")
        state["budget_violation"] = True

    return state 