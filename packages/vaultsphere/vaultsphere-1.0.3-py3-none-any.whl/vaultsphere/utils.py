from typing import Any, Dict

def apply_query_operator(value: Any, operator: str, query_val: Any) -> bool:
    if operator == "$gt":
        return value > query_val
    elif operator == "$gte":
        return value >= query_val
    elif operator == "$lt":
        return value < query_val
    elif operator == "$lte":
        return value <= query_val
    elif operator == "$ne":
        return value != query_val
    elif operator == "$in":
        
        try:
            return value in query_val
        except TypeError:
            return False
    elif operator == "$nin":
        
        try:
            return value not in query_val
        except TypeError:
            return True
    else:
        
        return value == query_val


def match_query(document: Dict[str, Any], query: Dict[str, Any]) -> bool:
    """
    Verifica si un documento cumple con todas las condiciones del query.
    El query puede tener condiciones simples o con operadores ($gt, $in, etc).
    """
    for key, condition in query.items():
        value = document.get(key)

        if isinstance(condition, dict):
            
            for op, v in condition.items():
                if not apply_query_operator(value, op, v):
                    return False
        else:
            
            if value != condition:
                return False

    return True
