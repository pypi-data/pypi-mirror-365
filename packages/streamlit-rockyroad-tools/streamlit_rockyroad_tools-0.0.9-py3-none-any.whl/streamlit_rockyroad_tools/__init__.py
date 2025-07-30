"""
Streamlit RockyRoad Tools - A collection of Streamlit components

This package provides various custom Streamlit components that can be easily
imported and used in your Streamlit applications.

Available components:
- st_notification_banner: A notification banner component with message and learn more link
"""

# Import all components to make them available at package level
from .st_notification_banner import st_notification_banner

# Define what gets imported with "from streamlit_rockyroad_tools import *"
__all__ = [
    'st_notification_banner',
]

# Package metadata
__version__ = '0.0.2'
__author__ = 'Your Name'
__description__ = 'A collection of Streamlit components'
