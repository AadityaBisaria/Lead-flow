from backend.utils.db_queries import run_query

def MemoryAgent(state: dict) -> dict:
    goals = state.get("user_goals", {})
    budget = goals.get("budget", 1000)
    memory_priority = goals.get("memory_priority", "medium")
    
    memory_weight_map = {"low": 0.1, "medium": 0.15, "high": 0.2}
    max_memory_price = budget * memory_weight_map.get(memory_priority, 0.15)
    
    # Calculate accumulated memory and modules from previous selections
    accumulated_memory = 0
    accumulated_modules = 0
    if "selected_parts" in state and "memory" in state["selected_parts"]:
        previous_memory = state["selected_parts"]["memory"]
        if isinstance(previous_memory, list):
            for mem in previous_memory:
                if "modules" in mem:
                    accumulated_memory += sum(module.get("capacity", 0) for module in mem["modules"])
                    accumulated_modules += len(mem["modules"])
        else:
            if "modules" in previous_memory:
                accumulated_memory += sum(module.get("capacity", 0) for module in previous_memory["modules"])
                accumulated_modules += len(previous_memory["modules"])
    
    # Calculate remaining memory needed
    target_memory = goals.get("min_memory", 0)
    remaining_memory = max(0, target_memory - accumulated_memory)
    
    # Build filter conditions
    filters = ["price <= %s"]
    params = [max_memory_price]
    
    # Handle specific RAM configuration if specified
    if "memory_config" in goals:
        config = goals["memory_config"]
        if isinstance(config, list):
            # User specified multiple configurations (e.g., ["2*32", "2*32"])
            current_config = config[len(state["selected_parts"].get("memory", []))]
            if "*" in current_config:
                modules, capacity = current_config.split("*")
                filters.append("array_length(modules, 1) = %s")
                params.append(int(modules))
                filters.append("modules[1]->>'capacity' = %s")
                params.append(capacity)
        else:
            # User specified single configuration (e.g., "4*32")
            if "*" in config:
                modules, capacity = config.split("*")
                filters.append("array_length(modules, 1) = %s")
                params.append(int(modules))
                filters.append("modules[1]->>'capacity' = %s")
                params.append(capacity)
    else:
        # No specific configuration, try to find a single kit that meets requirements
        if remaining_memory > 0:
            # Calculate optimal module count and capacity
            if "motherboard" in state["selected_parts"]:
                mb = state["selected_parts"]["motherboard"]
                available_slots = mb.get("memory_slots", 4) - accumulated_modules
                if available_slots > 0:
                    # Try to find a kit that can fit in remaining slots
                    filters.append("array_length(modules, 1) <= %s")
                    params.append(available_slots)
    
    # Speed requirements
    if "min_speed" in goals:
        filters.append("speed && ARRAY[%s]")
        params.append(goals["min_speed"])
    
    # Latency requirements
    if "max_cas_latency" in goals:
        filters.append("cas_latency <= %s")
        params.append(goals["max_cas_latency"])
    
    if "max_first_word_latency" in goals:
        filters.append("first_word_latency <= %s")
        params.append(goals["max_first_word_latency"])
    
    # Color preference
    if "memory_color" in goals:
        filters.append("color = %s")
        params.append(goals["memory_color"])
    
    # Preferred brand - using word boundary to match exact brand names
    brands = goals.get("preferred_memory_brands", [])
    if brands:
        brand_conditions = []
        for brand in brands:
            # Match brand at start of name or after a space
            brand_conditions.append("name ~* %s")
            params.append(f"\\m{brand}\\M|\\s{brand}\\M")
        filters.append(f"({' OR '.join(brand_conditions)})")
    
    filter_sql = " AND ".join(filters)
    
    query = f"""
    SELECT * FROM memory
    WHERE {filter_sql}
    ORDER BY 
        price_per_gb ASC,
        cas_latency ASC,
        first_word_latency ASC,
        speed[1] DESC
    LIMIT 1
    """
    
    results = run_query(query, params)
    
    if results:
        memory = results[0]
        
        # Add accumulated memory and modules to the memory properties
        memory["accumulated_memory"] = accumulated_memory
        memory["accumulated_modules"] = accumulated_modules
        
        # Store memory in selected_parts
        if "memory" not in state["selected_parts"]:
            state["selected_parts"]["memory"] = []
        state["selected_parts"]["memory"].append(memory)
        
        state["current_total_cost"] += memory["price"]
        state["part_attempt_log"]["memory"].append(memory["name"])
        
        # Check if we've reached the target memory
        total_memory = accumulated_memory + sum(module.get("capacity", 0) for module in memory["modules"])
        if total_memory >= target_memory:
            state["memory_target_reached"] = True
            
        # Check if we've completed all specified configurations
        if "memory_config" in goals and isinstance(goals["memory_config"], list):
            if len(state["selected_parts"]["memory"]) >= len(goals["memory_config"]):
                state["memory_target_reached"] = True
    else:
        state["compatibility_issues"].append("No compatible memory found.")
        state["budget_violation"] = True

    return state 