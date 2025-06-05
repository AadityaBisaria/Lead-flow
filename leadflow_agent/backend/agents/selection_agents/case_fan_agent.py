from backend.utils.db_queries import run_query

def CaseFanAgent(state: dict) -> dict:
    goals = state.get("user_goals", {})
    budget = goals.get("budget", 1000)
    fan_priority = goals.get("fan_priority", "medium")
    
    fan_weight_map = {"low": 0.02, "medium": 0.03, "high": 0.05}
    max_fan_price = budget * fan_weight_map.get(fan_priority, 0.03)
    
    # Build filter conditions
    filters = ["price <= %s"]
    params = [max_fan_price]
    
    # Size compatibility
    if "selected_parts" in state and "case" in state["selected_parts"]:
        case = state["selected_parts"]["case"]
        if "fan_sizes" in case:
            filters.append("size = ANY(%s)")
            params.append(case["fan_sizes"])
    
    # Color preference
    if "fan_color" in goals:
        filters.append("color = %s")
        params.append(goals["fan_color"])
    
    # RPM requirements
    if "min_rpm" in goals:
        filters.append("rpm[1] >= %s")  # Using first element of rpm array
        params.append(goals["min_rpm"])
    
    # Airflow requirements
    if "min_airflow" in goals:
        filters.append("airflow[1] >= %s")  # Using first element of airflow array
        params.append(goals["min_airflow"])
    
    # Noise level requirements
    if "max_noise" in goals:
        filters.append("noise_level[1] <= %s")  # Using first element of noise_level array
        params.append(goals["max_noise"])
    
    # PWM preference
    if "pwm_required" in goals:
        filters.append("pwm = %s")
        params.append(goals["pwm_required"])
    
    # Preferred brand
    brands = goals.get("preferred_fan_brands", [])
    if brands:
        brand_conditions = " OR ".join(["name ILIKE %s" for _ in brands])
        filters.append(f"({brand_conditions})")
        params.extend([f"%{brand}%" for brand in brands])
    
    filter_sql = " AND ".join(filters)
    
    query = f"""
    SELECT * FROM case_fan
    WHERE {filter_sql}
    ORDER BY 
        airflow[1] DESC,
        rpm[1] DESC,
        noise_level[1] ASC,
        price ASC
    LIMIT 1
    """
    
    results = run_query(query, params)
    
    if results:
        fan = results[0]
        state["selected_parts"]["case_fan"] = fan
        state["current_total_cost"] += fan["price"]
        state["part_attempt_log"]["case_fan"].append(fan["name"])
    else:
        state["compatibility_issues"].append("No compatible case fan found.")
        state["budget_violation"] = True

    return state 