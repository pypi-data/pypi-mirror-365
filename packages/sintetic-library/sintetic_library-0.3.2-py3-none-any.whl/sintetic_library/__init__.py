"""
Sintetic Client Library
Python library to interact with Sintetic GeoDB REST services.
"""

from .core import SinteticClient, TemporalResolution, SINTETIC_ENDPOINTS

__version__ = "0.3.0"
__author__ = "Leandro Rocchi"
__email__ = "leandro.rocchi@cnr.it"

# Supply the TemporalResolution enum for temporal resolution options
__all__ = [
    "SinteticClient",
    "TemporalResolution",
    "SINTETIC_ENDPOINTS"
]