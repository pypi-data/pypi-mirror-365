def parse_filter(filter_str: str):
    rules = []
    for part in filter_str.split(';'):
        if not part:
            continue
        include = part.startswith('+')
        rule_str = part[1:]
        path_pattern, method = (rule_str.split(':') + [None])[:2]
        
        # Convert glob-like pattern to regex
        regex_pattern = '^' + path_pattern.replace('**', '.*').replace('*', '[^/]+') + '$'
        rules.append({
            "include": include,
            "regex": regex_pattern,
            "method": method.upper() if method else None
        })

    def filter_func(path: str, method: str) -> bool:
        import re
        included = None
        for rule in rules:
            if re.match(rule["regex"], path):
                if rule["method"] and rule["method"] != method.upper():
                    continue
                included = rule["include"]
        
        return included if included is not None else True

    return filter_func
