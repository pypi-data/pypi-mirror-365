"""
`pylib25` is a simple library to illustrate how to deploy a Python library.
"""

def sqr(x: float) -> float:
    """
    Get square of the given `x`.

    ```
    from pylib25 import sqr

    assert sqr(5.0) == 25.0
    ```
    """
    return x ** 2
