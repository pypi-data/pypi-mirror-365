import re
from collections import defaultdict
from restful_checker.checks.check_result import CheckResult

def check_param_consistency(all_paths: dict) -> tuple[list[str], float]:
    """
    Check for consistent path parameter naming across the OpenAPI spec.

    - Detects parameters with same meaning but different casing (e.g., {UserId}, {user_id})
    - Flags mixed naming styles (snake_case vs camelCase)
    - Warns about overly generic names (e.g., {id}, {name})

    Args:
        all_paths (dict): The full OpenAPI "paths" section.

    Returns:
        tuple[list[str], float]: A list of messages and the computed score.
    """
    result = CheckResult("param_consistency")
    param_map = defaultdict(set)
    all_params = set()

    # Extract all path parameters
    for path in all_paths.keys():
        for match in re.finditer(r"\{([^}]+)}", path):
            param = match.group(1)
            param_map[param.lower()].add(param)
            all_params.add(param)

    # Check inconsistent casing for same parameter
    for variations in param_map.values():
        if len(variations) > 1:
            group_list = ", ".join(sorted(variations))
            result.warning(f"Inconsistent parameter naming: {group_list}")

    # Check style conflicts
    snake_case = {p for p in all_params if "_" in p}
    camel_case = {p for p in all_params if re.search(r"[a-z][A-Z]", p)}

    if snake_case and camel_case:
        result.warning("Mixed parameter styles detected (snake_case and camelCase)")

    # Warn on generic parameter names
    for param in all_params:
        if param.lower() in {"id", "name", "value"}:
            result.warning(f"Generic parameter name used: `{param}` — consider using more specific names")

    if not result.messages:
        result.success("Path parameters look consistent")

    return result.messages, result.finalize_score()
