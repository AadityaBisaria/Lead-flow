from backend.utils.db_queries import run_query

def WirelessNetworkCardAgent(state: dict) -> dict:
    goals = state.get("user_goals", {})
    budget = goals.get("budget", 1000)
    network_priority = goals.get("network_priority", "medium")
    
    network_weight_map = {"low": 0.01, "medium": 0.02, "high": 0.03}
    max_network_price = budget * network_weight_map.get(network_priority, 0.02)
    
    # Build filter conditions
    filters = ["price <= %s"]
    params = [max_network_price]
    
    # Protocol requirements (e.g., 802.11ac, 802.11ax)
    if "wireless_protocol" in goals:
        filters.append("protocol = %s")
        params.append(goals["wireless_protocol"])
    
    # Interface type
    if "interface_type" in goals:
        filters.append("interface = %s")
        params.append(goals["interface_type"])
    
    # Color preference
    if "color" in goals:
        filters.append("color = %s")
        params.append(goals["color"])
    
    # Preferred brand
    brands = goals.get("preferred_network_brands", [])
    if brands:
        brand_conditions = " OR ".join(["name ILIKE %s" for _ in brands])
        filters.append(f"({brand_conditions})")
        params.extend([f"%{brand}%" for brand in brands])
    
    filter_sql = " AND ".join(filters)
    
    query = f"""
    SELECT * FROM wireless_network_card
    WHERE {filter_sql}
    ORDER BY 
        protocol DESC,
        price ASC
    LIMIT 1
    """
    
    results = run_query(query, params)
    
    if results:
        network_card = results[0]
        state["selected_parts"]["wireless_network_card"] = network_card
        state["current_total_cost"] += network_card["price"]
        state["part_attempt_log"]["wireless_network_card"].append(network_card["name"])
    else:
        state["compatibility_issues"].append("No compatible wireless network card found.")
        state["budget_violation"] = True

    return state 