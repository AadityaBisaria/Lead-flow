from backend.utils.db_queries import run_query

def UPSAgent(state: dict) -> dict:
    goals = state.get("user_goals", {})
    budget = goals.get("budget", 1000)
    ups_priority = goals.get("ups_priority", "medium")
    
    ups_weight_map = {"low": 0.05, "medium": 0.08, "high": 0.12}
    max_ups_price = budget * ups_weight_map.get(ups_priority, 0.08)
    
    # Build filter conditions
    filters = ["price <= %s"]
    params = [max_ups_price]
    
    # Power capacity requirements (in watts)
    if "selected_parts" in state and "power_supply" in state["selected_parts"]:
        psu = state["selected_parts"]["power_supply"]
        min_power = psu["wattage"] * 1.2  # 20% buffer
        filters.append("capacity_w >= %s")
        params.append(min_power)
    
    # VA capacity requirements
    if "min_va" in goals:
        filters.append("capacity_va >= %s")
        params.append(goals["min_va"])
    
    # Preferred brand
    brands = goals.get("preferred_ups_brands", [])
    if brands:
        brand_conditions = " OR ".join(["name ILIKE %s" for _ in brands])
        filters.append(f"({brand_conditions})")
        params.extend([f"%{brand}%" for brand in brands])
    
    filter_sql = " AND ".join(filters)
    
    query = f"""
    SELECT * FROM ups
    WHERE {filter_sql}
    ORDER BY 
        capacity_w DESC,
        capacity_va DESC,
        price ASC
    LIMIT 1
    """
    
    results = run_query(query, params)
    
    if results:
        ups = results[0]
        state["selected_parts"]["ups"] = ups
        state["current_total_cost"] += ups["price"]
        state["part_attempt_log"]["ups"].append(ups["name"])
    else:
        state["compatibility_issues"].append("No compatible UPS found.")
        state["budget_violation"] = True

    return state 