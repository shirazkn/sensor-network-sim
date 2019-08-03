"""
Some helper functions to handle the math/methods involved in the classes
"""

def column(vector):
    """
    Recast into a column vector
    """
    return vector.reshape(len(vector), 1)