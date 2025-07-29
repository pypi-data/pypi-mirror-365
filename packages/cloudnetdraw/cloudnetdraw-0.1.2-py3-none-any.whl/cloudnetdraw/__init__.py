"""
CloudNet Draw - Azure VNet topology visualization tool
"""
try:
    from importlib.metadata import version
except ImportError:
    # Python < 3.8
    from importlib_metadata import version

__version__ = version("cloudnetdraw")