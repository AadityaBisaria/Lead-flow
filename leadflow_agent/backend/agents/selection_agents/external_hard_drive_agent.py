from backend.utils.db_queries import run_query

def ExternalHardDriveAgent(state: dict) -> dict:
    goals = state.get("user_goals", {})
    budget = goals.get("budget", 1000)
    drive_priority = goals.get("drive_priority", "medium")
    
    drive_weight_map = {"low": 0.05, "medium": 0.08, "high": 0.12}
    max_drive_price = budget * drive_weight_map.get(drive_priority, 0.08)
    
    # Build filter conditions
    filters = ["price <= %s"]
    params = [max_drive_price]
    
    # Capacity requirements
    if "min_capacity" in goals:
        filters.append("capacity >= %s")
        params.append(goals["min_capacity"])
    
    # Interface type
    if "interface" in goals:
        filters.append("interface = %s")
        params.append(goals["interface"])
    
    # Drive type preference
    if "drive_type" in goals:
        filters.append("type = %s")
        params.append(goals["drive_type"])
    
    # Color preference
    if "drive_color" in goals:
        filters.append("color = %s")
        params.append(goals["drive_color"])
    
    # Preferred brand
    brands = goals.get("preferred_drive_brands", [])
    if brands:
        brand_conditions = " OR ".join(["name ILIKE %s" for _ in brands])
        filters.append(f"({brand_conditions})")
        params.extend([f"%{brand}%" for brand in brands])
    
    filter_sql = " AND ".join(filters)
    
    query = f"""
    SELECT * FROM external_hard_drive
    WHERE {filter_sql}
    ORDER BY 
        CASE 
            WHEN type = 'SSD' THEN 1
            WHEN type = 'HDD' THEN 2
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
        state["selected_parts"]["external_hard_drive"] = drive
        state["current_total_cost"] += drive["price"]
        state["part_attempt_log"]["external_hard_drive"].append(drive["name"])
    else:
        state["compatibility_issues"].append("No compatible external hard drive found.")
        state["budget_violation"] = True

    return state 