"""
Streamlit RockyRoad Tools - A collection of Streamlit components

This package provides various custom Streamlit components that can be easily
imported and used in your Streamlit applications.

Available components:
- st_notification_bar: A notification bar component with message and learn more link
"""

# Import all components to make them available at package level
from .st_notification_bar import st_notification_bar

# Define what gets imported with "from streamlit_rockyroad_tools import *"
__all__ = [
    'st_notification_bar',
]

# Package metadata
__version__ = '0.0.2'
__author__ = 'Your Name'
__description__ = 'A collection of Streamlit components'
