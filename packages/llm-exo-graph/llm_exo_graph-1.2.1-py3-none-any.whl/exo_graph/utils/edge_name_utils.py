"""
Edge Name Utilities - Convert between edge name formats

Provides utility functions to convert between UPPER_CASE and natural language 
edge name formats for improved readability and embedding accuracy.
"""


def to_natural(edge_name: str) -> str:
    """
    Convert UPPER_CASE edge name to natural language format.
    
    Examples:
        LIVES_IN -> "lives in"
        WORKS_AT -> "works at" 
        IS_EMPLOYED_BY -> "is employed by"
    
    Args:
        edge_name: Edge name in UPPER_CASE_FORMAT
        
    Returns:
        Natural language version in lowercase
    """
    if not edge_name:
        return ""
    
    # Convert to lowercase and replace underscores with spaces
    natural = edge_name.lower().replace('_', ' ')
    
    # Clean up any multiple spaces
    natural = ' '.join(natural.split())
    
    return natural.strip()


def to_edge_name(natural_name: str) -> str:
    """
    Convert natural language edge name to UPPER_CASE format.
    
    Examples:
        "lives in" -> LIVES_IN
        "works at" -> WORKS_AT
        "is employed by" -> IS_EMPLOYED_BY
    
    Args:
        natural_name: Edge name in natural language format
        
    Returns:
        UPPER_CASE_FORMAT version
    """
    if not natural_name:
        return ""
    
    # Convert to uppercase and replace spaces with underscores
    upper_case = natural_name.upper().replace(' ', '_')
    
    # Clean up any multiple underscores
    while '__' in upper_case:
        upper_case = upper_case.replace('__', '_')
    
    return upper_case.strip('_')