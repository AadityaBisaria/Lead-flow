from backend.utils.db_queries import run_query

def NetworkCardAgent(state: dict) -> dict:
    goals = state.get("user_goals", {})
    budget = goals.get("budget", 1000)
    network_priority = goals.get("network_priority", "medium")
    
    network_weight_map = {"low": 0.02, "medium": 0.03, "high": 0.05}
    max_network_price = budget * network_weight_map.get(network_priority, 0.03)
    
    # Build filter conditions
    filters = ["price <= %s"]
    params = [max_network_price]
    
    # Network type preference
    if "network_type" in goals:
        filters.append("type = %s")
        params.append(goals["network_type"])
    
    # Interface compatibility with motherboard
    if "selected_parts" in state and "motherboard" in state["selected_parts"]:
        motherboard = state["selected_parts"]["motherboard"]
        filters.append("interface IN (SELECT unnest(%s))")
        params.append(motherboard["expansion_slots"])
    
    # Wireless specific requirements
    if goals.get("require_wifi"):
        filters.append("type = 'wireless'")
        if "min_wifi_speed" in goals:
            filters.append("speed >= %s")
            params.append(goals["min_wifi_speed"])
    
    # Wired specific requirements
    if goals.get("require_ethernet"):
        filters.append("type = 'wired'")
        if "min_ethernet_speed" in goals:
            filters.append("speed >= %s")
            params.append(goals["min_ethernet_speed"])
    
    # Preferred brand
    brands = goals.get("preferred_network_brands", [])
    if brands:
        brand_conditions = " OR ".join(["name ILIKE %s" for _ in brands])
        filters.append(f"({brand_conditions})")
        params.extend([f"%{brand}%" for brand in brands])
    
    filter_sql = " AND ".join(filters)
    
    query = f"""
    SELECT * FROM (
        SELECT * FROM wireless_network_card
        UNION ALL
        SELECT * FROM wired_network_card
    ) network_cards
    WHERE {filter_sql}
    ORDER BY speed DESC, price ASC
    LIMIT 1
    """
    
    results = run_query(query, params)
    
    if results:
        network_card = results[0]
        state["selected_parts"]["network_card"] = network_card
        state["current_total_cost"] += network_card["price"]
        state["part_attempt_log"]["network_card"].append(network_card["name"])
    else:
        state["compatibility_issues"].append("No compatible network card found.")
        state["budget_violation"] = True

    return state 