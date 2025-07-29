"""
This module provides helper functions for parsing and resolving OpenAPI specs.
"""

def resolve_ref(spec: dict, ref: str) -> dict:
    """
    Resolves a JSON Pointer reference ($ref) within the specification.
    e.g., "#/components/schemas/Pet" -> spec['components']['schemas']['Pet']
    """
    if not ref.startswith('#/'):
        # We'll only handle internal, root-level references for now.
        return {}
    
    keys = ref[2:].split('/')
    node = spec
    try:
        for key in keys:
            node = node[key]
        return node
    except (KeyError, TypeError):
        # The reference was not found
        return {}
