class FilterError(Exception):
    pass


class RootKeyUsedError(FilterError):
    """Raise when reserved root key is used for memberOf-Field"""


class NoGroupOrCondition(FilterError):
    """Raise when a filter is neither Group nor Condition"""
