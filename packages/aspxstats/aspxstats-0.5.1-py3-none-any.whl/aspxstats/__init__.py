from .exceptions import Error, ClientError, TimeoutError, InvalidResponseError, NotFoundError, InvalidParameterError, \
    ValidationError
from .types import ResponseValidationMode

"""
aspxstats.
Python library for retrieving stats of Battlefield 2 and Battlefield 2142 players.
"""

__version__ = '0.5.1'
__author__ = 'cetteup'
__credits__ = 'wilson212'
__all__ = [
    'bf2',
    'ResponseValidationMode',
    'Error',
    'ClientError',
    'TimeoutError',
    'InvalidResponseError',
    'ValidationError',
    'NotFoundError',
    'InvalidParameterError'
]
