class Error(Exception):
    """Base class for errors"""
    pass


class InvalidSensorClass(Error):
    """
    Your sensor class probably doesn't have all the methods they're expected to have.
    """
    pass
