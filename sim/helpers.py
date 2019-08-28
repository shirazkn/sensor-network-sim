"""
Some helper functions to handle the math/methods involved in the sim
"""


def column(vector):
    """
    Recast into a column vector
    """
    return vector.reshape(len(vector), 1)


def make_dir(location):
    """
    Note, will not handle building of intermediate dirs
    """
    if not os.path.isdir(location):
        os.mkdir(location)
