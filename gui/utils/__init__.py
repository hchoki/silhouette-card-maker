"""
Utils package - Shared utilities for the GUI

Contains:
- settings_manager: Settings persistence
- styles: UI styling configuration
- threading_utils: Thread-safe message queue handling
"""

from gui.utils.settings_manager import SettingsManager
from gui.utils.styles import StyleManager

__all__ = ['SettingsManager', 'StyleManager']
