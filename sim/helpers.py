"""
Some helper functions to handle the math/methods
"""
import os


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


def get_unique_ids(length):
    # TODO
    # Using MATLAB indexing for now
    return [str(_id) for _id in range(1, length + 1)]
