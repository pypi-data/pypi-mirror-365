import numpy as np
from .base import gini_coefficient

def get_dimension_data(Portfolios, dimensions, dimension_name):
    """
    Get data for a specific dimension.
    Args:
        Portfolios: 2D array of agent portfolios
        dimensions: List of dimension names
        dimension_name: Name of the dimension to extract
    Returns:
        Array of values for that dimension across all agents
    """
    if dimension_name not in dimensions:
        raise ValueError(f"Dimension '{dimension_name}' not found. Available dimensions: {dimensions}")
    dim_idx = dimensions.index(dimension_name)
    return Portfolios[:, dim_idx]

def get_leverage_data(Portfolios, dimensions, c_leverage_factor, xp_module):
    """
    Get current leverage values for all agents.
    Returns:
        Array of leverage coefficients
    """
    try:
        knowledge_idx = dimensions.index('knowledge')
        knowledge_capital = Portfolios[:, knowledge_idx]
    except ValueError:
        knowledge_capital = Portfolios[:, 0]
    return 1.0 + c_leverage_factor * knowledge_capital

def get_focus_data(Focus, dimensions, dimension_name):
    """
    Get focus values for a specific dimension.
    Args:
        Focus: 2D array of focus values
        dimensions: List of dimension names
        dimension_name: Name of the dimension
    Returns:
        Array of focus values for that dimension
    """
    if dimension_name not in dimensions:
        raise ValueError(f"Dimension '{dimension_name}' not found. Available dimensions: {dimensions}")
    dim_idx = dimensions.index(dimension_name)
    return Focus[:, dim_idx]

def get_gini_coefficients(Portfolios, AgentWealth, dimensions, xp_module):
    """
    Calculate Gini coefficients for all dimensions.
    Returns:
        Dictionary mapping dimension names to Gini coefficients
    """
    gini_dict = {}
    for dim_name in dimensions:
        dim_data = get_dimension_data(Portfolios, dimensions, dim_name)
        gini_dict[dim_name] = gini_coefficient(dim_data, xp_module)
    gini_dict['total'] = gini_coefficient(AgentWealth, xp_module)
    return gini_dict

def get_average_leverage(Portfolios, dimensions, c_leverage_factor, xp_module):
    """
    Calculate average leverage across all agents.
    Returns:
        Average leverage value
    """
    leverage_data = get_leverage_data(Portfolios, dimensions, c_leverage_factor, xp_module)
    return xp_module.mean(leverage_data) 