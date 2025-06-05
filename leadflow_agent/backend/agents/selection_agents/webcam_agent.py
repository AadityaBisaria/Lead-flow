from backend.utils.db_queries import run_query

def WebcamAgent(state: dict) -> dict:
    goals = state.get("user_goals", {})
    budget = goals.get("budget", 1000)
    webcam_priority = goals.get("webcam_priority", "medium")
    
    webcam_weight_map = {"low": 0.02, "medium": 0.03, "high": 0.05}
    max_webcam_price = budget * webcam_weight_map.get(webcam_priority, 0.03)
    
    # Build filter conditions
    filters = ["price <= %s"]
    params = [max_webcam_price]
    
    # Resolution requirements
    if "min_resolution" in goals:
        filters.append("%s = ANY(resolutions)")
        params.append(goals["min_resolution"])
    
    # Connection type
    if "connection_type" in goals:
        filters.append("connection = %s")
        params.append(goals["connection_type"])
    
    # Focus type preference
    if "focus_type" in goals:
        filters.append("focus_type = %s")
        params.append(goals["focus_type"])
    
    # OS compatibility
    if "selected_parts" in state and "operating_system" in state["selected_parts"]:
        os = state["selected_parts"]["operating_system"]
        filters.append("%s = ANY(os)")
        params.append(os["name"])
    
    # Field of view requirements
    if "min_fov" in goals:
        filters.append("fov >= %s")
        params.append(goals["min_fov"])
    
    # Preferred brand
    brands = goals.get("preferred_webcam_brands", [])
    if brands:
        brand_conditions = " OR ".join(["name ILIKE %s" for _ in brands])
        filters.append(f"({brand_conditions})")
        params.extend([f"%{brand}%" for brand in brands])
    
    filter_sql = " AND ".join(filters)
    
    query = f"""
    SELECT * FROM webcam
    WHERE {filter_sql}
    ORDER BY 
        fov DESC,
        price ASC
    LIMIT 1
    """
    
    results = run_query(query, params)
    
    if results:
        webcam = results[0]
        state["selected_parts"]["webcam"] = webcam
        state["current_total_cost"] += webcam["price"]
        state["part_attempt_log"]["webcam"].append(webcam["name"])
    else:
        state["compatibility_issues"].append("No compatible webcam found.")
        state["budget_violation"] = True

    return state 