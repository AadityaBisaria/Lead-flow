from backend.utils.db_queries import run_query

def OpticalDriveAgent(state: dict) -> dict:
    goals = state.get("user_goals", {})
    budget = goals.get("budget", 1000)
    drive_priority = goals.get("drive_priority", "medium")
    
    drive_weight_map = {"low": 0.02, "medium": 0.03, "high": 0.05}
    max_drive_price = budget * drive_weight_map.get(drive_priority, 0.03)
    
    # Build filter conditions
    filters = ["price <= %s"]
    params = [max_drive_price]
    
    # BD requirements
    if "bd_required" in goals:
        filters.append("bd > 0")
    
    # DVD requirements
    if "dvd_required" in goals:
        filters.append("dvd > 0")
    
    # CD requirements
    if "cd_required" in goals:
        filters.append("cd > 0")
    
    # BD write capability
    if "bd_write_required" in goals:
        filters.append("bd_write = 'Yes'")
    
    # DVD write capability
    if "dvd_write_required" in goals:
        filters.append("dvd_write = 'Yes'")
    
    # CD write capability
    if "cd_write_required" in goals:
        filters.append("cd_write = 'Yes'")
    
    # Preferred brand
    brands = goals.get("preferred_drive_brands", [])
    if brands:
        brand_conditions = " OR ".join(["name ILIKE %s" for _ in brands])
        filters.append(f"({brand_conditions})")
        params.extend([f"%{brand}%" for brand in brands])
    
    filter_sql = " AND ".join(filters)
    
    query = f"""
    SELECT * FROM optical_drive
    WHERE {filter_sql}
    ORDER BY 
        bd DESC,
        dvd DESC,
        cd DESC,
        price ASC
    LIMIT 1
    """
    
    results = run_query(query, params)
    
    if results:
        drive = results[0]
        state["selected_parts"]["optical_drive"] = drive
        state["current_total_cost"] += drive["price"]
        state["part_attempt_log"]["optical_drive"].append(drive["name"])
    else:
        state["compatibility_issues"].append("No compatible optical drive found.")
        state["budget_violation"] = True

    return state 