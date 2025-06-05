from backend.utils.db_queries import run_query

def CPUAgent(state: dict) -> dict:
    goals = state.get("user_goals", {})
    budget = goals.get("budget", 1000)
    cpu_priority = goals.get("cpu_priority", "medium")
    
    cpu_weight_map = {"low": 0.2, "medium": 0.3, "high": 0.5}
    max_cpu_price = budget * cpu_weight_map.get(cpu_priority, 0.3)
    
    # Build filter conditions
    filters = ["price <= %s"]
    params = [max_cpu_price]
    
    # Minimum cores
    if "min_cores" in goals:
        filters.append("core_count >= %s")
        params.append(goals["min_cores"])
    
    # Core clock requirements
    if "cpu_min_core_clock" in goals:
        filters.append("core_clock >= %s")
        params.append(goals["cpu_min_core_clock"])
    
    # Boost clock requirements
    if "cpu_min_boost_clock" in goals:
        filters.append("boost_clock >= %s")
        params.append(goals["cpu_min_boost_clock"])
    
    # TDP requirements
    if "max_tdp" in goals:
        filters.append("tdp <= %s")
        params.append(goals["max_tdp"])
    
    # SMT (simultaneous multithreading)
    if goals.get("require_smt"):
        filters.append("smt = TRUE")
    
    # Integrated graphics required
    if goals.get("require_igpu"):
        filters.append("graphics IS NOT NULL AND graphics != 'None'")
    
    # Preferred brand (e.g. name ILIKE '%AMD%')
    brands = goals.get("preferred_cpu_brands", [])
    if brands:
        brand_conditions = " OR ".join(["name ILIKE %s" for _ in brands])
        filters.append(f"({brand_conditions})")
        params.extend([f"%{brand}%" for brand in brands])
    
    filter_sql = " AND ".join(filters)
    
    query = f"""
    SELECT * FROM cpu
    WHERE {filter_sql}
    ORDER BY 
        core_count DESC,
        boost_clock DESC,
        core_clock DESC,
        tdp ASC,
        price ASC
    LIMIT 1
    """
    
    results = run_query(query, params)
    
    if results:
        cpu = results[0]
        state["selected_parts"]["cpu"] = cpu
        state["current_total_cost"] += cpu["price"]
        state["part_attempt_log"]["cpu"].append(cpu["name"])
    else:
        state["compatibility_issues"].append("No CPU found that matches constraints.")
        state["budget_violation"] = True

    return state
