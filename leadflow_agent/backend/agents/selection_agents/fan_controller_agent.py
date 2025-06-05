from backend.utils.db_queries import run_query

def FanControllerAgent(state: dict) -> dict:
    goals = state.get("user_goals", {})
    budget = goals.get("budget", 1000)
    controller_priority = goals.get("controller_priority", "medium")
    
    controller_weight_map = {"low": 0.02, "medium": 0.03, "high": 0.05}
    max_controller_price = budget * controller_weight_map.get(controller_priority, 0.03)
    
    # Build filter conditions
    filters = ["price <= %s"]
    params = [max_controller_price]
    
    # Channel count requirements
    if "min_channels" in goals:
        filters.append("channels >= %s")
        params.append(goals["min_channels"])
    
    # PWM requirement
    if goals.get("require_pwm"):
        filters.append("pwm = TRUE")
    
    # Form factor compatibility with case
    if "selected_parts" in state and "case" in state["selected_parts"]:
        case = state["selected_parts"]["case"]
        filters.append("form_factor && %s")
        params.append(case["fan_controller_form_factors"])
    
    # Color preference
    if "controller_color" in goals:
        filters.append("color = %s")
        params.append(goals["controller_color"])
    
    # Preferred brand
    brands = goals.get("preferred_controller_brands", [])
    if brands:
        brand_conditions = " OR ".join(["name ILIKE %s" for _ in brands])
        filters.append(f"({brand_conditions})")
        params.extend([f"%{brand}%" for brand in brands])
    
    filter_sql = " AND ".join(filters)
    
    query = f"""
    SELECT * FROM fan_controller
    WHERE {filter_sql}
    ORDER BY 
        channels DESC,
        channel_wattage DESC,
        CASE 
            WHEN pwm = TRUE THEN 1
            ELSE 2
        END,
        price ASC
    LIMIT 1
    """
    
    results = run_query(query, params)
    
    if results:
        controller = results[0]
        state["selected_parts"]["fan_controller"] = controller
        state["current_total_cost"] += controller["price"]
        state["part_attempt_log"]["fan_controller"].append(controller["name"])
    else:
        state["compatibility_issues"].append("No compatible fan controller found.")
        state["budget_violation"] = True

    return state 