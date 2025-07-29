def explore_json_aggregated(obj, level_name="ROOT", depth=0, seen_levels=None):
    """Enhanced JSON explorer with correct item counting"""
    if seen_levels is None:
        seen_levels = {}
    
    all_values = {}
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            if not isinstance(value, (dict, list)):
                field_key = key
                if field_key not in all_values:
                    all_values[field_key] = set()
                all_values[field_key].add(value)
            elif isinstance(value, list):
                # Initialize level if not seen
                if level_name not in seen_levels:
                    seen_levels[level_name] = {'_instances': [], '_field_counts': {}, '_list_stats': {}}
                
                # Track this specific list instance
                seen_levels[level_name]['_instances'].append(len(value))
                
                # Track empty vs non-empty for this specific list
                if key not in seen_levels[level_name]['_list_stats']:
                    seen_levels[level_name]['_list_stats'][key] = {'empty': 0, 'non_empty': 0}
                
                if len(value) == 0:
                    seen_levels[level_name]['_list_stats'][key]['empty'] += 1
                else:
                    seen_levels[level_name]['_list_stats'][key]['non_empty'] += 1
                
                nested_values = explore_json_aggregated(value, key, depth + 1, seen_levels)
                for k, v in nested_values.items():
                    if k not in all_values:
                        all_values[k] = set()
                    all_values[k].update(v)
            elif isinstance(value, dict):
                nested_values = explore_json_aggregated(value, key, depth + 1, seen_levels)
                for k, v in nested_values.items():
                    if k not in all_values:
                        all_values[k] = set()
                    all_values[k].update(v)
    
    elif isinstance(obj, list):
        # Initialize level tracking if not exists
        if level_name not in seen_levels:
            seen_levels[level_name] = {'_instances': [], '_field_counts': {}, '_list_stats': {}}
        
        # Count ONLY dict items in this list (ignore other types)
        dict_items = [item for item in obj if isinstance(item, dict)]
        
        # Track this specific list instance
        seen_levels[level_name]['_instances'].append(len(dict_items))
        
        # Process every dict item in the list
        for item in dict_items:
            # Track field presence in this specific item
            for key in item.keys():
                if key not in seen_levels[level_name]['_field_counts']:
                    seen_levels[level_name]['_field_counts'][key] = 0
                seen_levels[level_name]['_field_counts'][key] += 1
            
            # Process field values and types  
            for key, value in item.items():
                if key not in seen_levels[level_name]:
                    seen_levels[level_name][key] = set()
                seen_levels[level_name][key].add(type(value).__name__)
                
                if not isinstance(value, (dict, list)):
                    field_key = key
                    if field_key not in all_values:
                        all_values[field_key] = set()
                    all_values[field_key].add(value)
                elif isinstance(value, list):
                    # Track empty vs non-empty lists
                    if key not in seen_levels[level_name]['_list_stats']:
                        seen_levels[level_name]['_list_stats'][key] = {'empty': 0, 'non_empty': 0}
                    
                    if len(value) == 0:
                        seen_levels[level_name]['_list_stats'][key]['empty'] += 1
                    else:
                        seen_levels[level_name]['_list_stats'][key]['non_empty'] += 1
                    
                    nested_values = explore_json_aggregated(value, key, depth + 1, seen_levels)
                    for k, v in nested_values.items():
                        if k not in all_values:
                            all_values[k] = set()
                        all_values[k].update(v)
                elif isinstance(value, dict):
                    nested_values = explore_json_aggregated(value, key, depth + 1, seen_levels)
                    for k, v in nested_values.items():
                        if k not in all_values:
                            all_values[k] = set()
                        all_values[k].update(v)
    
    # Print results only at the top level
    if depth == 0:
        print("=== AGGREGATED STRUCTURE ===")
        for level, level_data in seen_levels.items():
            # Calculate total items across all instances of this level
            instances = level_data.get('_instances', [])
            total_items = sum(instances)
            num_instances = len(instances)
            
            field_counts = level_data.get('_field_counts', {})
            list_stats = level_data.get('_list_stats', {})
            
            print(f"{level}[] (total items: {total_items} across {num_instances} list instances):")
            
            for field, types in sorted(level_data.items()):
                if field.startswith('_'):  # Skip metadata fields
                    continue
                    
                type_str = "/".join(sorted(types)) if len(types) > 1 else list(types)[0]
                presence_count = field_counts.get(field, 0)
                presence_pct = (presence_count / total_items * 100) if total_items > 0 else 0
                
                # Add empty list warning for list fields
                empty_warning = ""
                if field in list_stats:
                    stats = list_stats[field]
                    if stats['empty'] > 0:
                        total_lists = stats['empty'] + stats['non_empty']
                        empty_pct = (stats['empty'] / total_lists * 100)
                        empty_warning = f" [WARNING: {stats['empty']}/{total_lists} lists empty ({empty_pct:.1f}%)]"
                
                print(f"  {field}: {type_str} ({presence_pct:.1f}% present){empty_warning}")
            print()
        
        # Convert sets to sorted lists for return dictionary
        return_dict = {}
        for field, values in all_values.items():
            if isinstance(values, set):
                try:
                    return_dict[field] = sorted(list(values))
                except TypeError:
                    return_dict[field] = sorted(list(values), key=str)
            else:
                return_dict[field] = values
        
        return return_dict
    
    return all_values