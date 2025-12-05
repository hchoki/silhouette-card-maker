"""
User Data Directory Management

Handles the location of user data directories for the packaged application.
Uses platform-appropriate locations for storing user data.
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional


class UserDataManager:
    """Manages user data directory locations for the application."""
    
    def __init__(self):
        self._user_data_dir: Optional[Path] = None
        self._is_frozen = getattr(sys, 'frozen', False)
        self._config_loaded = False
        
    def get_config_dir(self) -> Path:
        """
        Get the configuration directory path for settings and offset profiles.
        This is always in APPDATA for packaged apps, regardless of user data location.
        
        Returns:
            Path: The configuration directory
        """
        if self._is_frozen:
            # Packaged executable - use config in APPDATA
            if sys.platform == 'win32':
                base_dir = os.getenv('APPDATA', os.path.expanduser('~'))
                config_dir = Path(base_dir) / 'SilhouetteCardMaker' / 'config'
            elif sys.platform == 'darwin':
                config_dir = Path.home() / 'Library' / 'Application Support' / 'SilhouetteCardMaker' / 'config'
            else:
                xdg_data_home = os.getenv('XDG_DATA_HOME', os.path.join(os.path.expanduser('~'), '.local', 'share'))
                config_dir = Path(xdg_data_home) / 'SilhouetteCardMaker' / 'config'
        else:
            # Development mode - use repository's data directory
            if getattr(sys, '_MEIPASS', None):
                repo_root = Path(sys._MEIPASS)
            else:
                repo_root = Path(__file__).parent.parent.parent
            config_dir = repo_root / 'data'
        
        # Ensure the directory exists
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    def get_default_root_suggestion(self) -> Path:
        """
        Get the suggested default root directory (where the exe is located).
        
        Returns:
            Path: Suggested root directory
        """
        if self._is_frozen:
            # Packaged executable - suggest exe directory
            if getattr(sys, '_MEIPASS', None):
                # Running from PyInstaller bundle
                exe_path = Path(sys.executable).parent
            else:
                exe_path = Path(sys.executable).parent
            return exe_path
        else:
            # Development mode - use repository's game directory
            repo_root = Path(__file__).parent.parent.parent
            return repo_root / 'game'
    
    def load_user_data_location(self) -> Optional[Path]:
        """
        Load the user-selected data directory from config.
        
        Returns:
            Optional[Path]: The saved user data directory, or None if not set
        """
        config_dir = self.get_config_dir()
        location_file = config_dir / 'data_location.json'
        
        if location_file.exists():
            try:
                with open(location_file, 'r') as f:
                    data = json.load(f)
                    path = Path(data.get('user_data_dir', ''))
                    if path.exists():
                        return path
            except (json.JSONDecodeError, OSError):
                pass
        
        return None
    
    def save_user_data_location(self, path: Path) -> None:
        """
        Save the user-selected data directory to config.
        
        Args:
            path: The user data directory path to save
        """
        config_dir = self.get_config_dir()
        location_file = config_dir / 'data_location.json'
        
        with open(location_file, 'w') as f:
            json.dump({
                'user_data_dir': str(path),
                'configured': True
            }, f, indent=2)
    
    def is_configured(self) -> bool:
        """
        Check if user has configured their data directory.
        
        Returns:
            bool: True if configured
        """
        config_dir = self.get_config_dir()
        location_file = config_dir / 'data_location.json'
        return location_file.exists()
        
    def get_user_data_dir(self) -> Path:
        """
        Get the user data directory path.
        
        For packaged executables:
        - First checks for user-configured location
        - Falls back to exe directory if not configured
        
        For development, uses the repository's game/ directory.
        
        Returns:
            Path: The user data directory
        """
        if self._user_data_dir is not None:
            return self._user_data_dir
        
        if not self._config_loaded:
            # Try to load saved location (only for packaged apps)
            if self._is_frozen:
                saved_location = self.load_user_data_location()
                if saved_location:
                    self._user_data_dir = saved_location
                    self._config_loaded = True
                    return self._user_data_dir
            
            self._config_loaded = True
        
        if self._is_frozen:
            # Packaged executable - use default suggestion (exe directory)
            self._user_data_dir = self.get_default_root_suggestion()
        else:
            # Development mode - use repository's game directory
            if getattr(sys, '_MEIPASS', None):
                repo_root = Path(sys._MEIPASS)
            else:
                repo_root = Path(__file__).parent.parent.parent
            self._user_data_dir = repo_root / 'game'
        
        return self._user_data_dir
    
    def set_user_data_dir(self, path: Path) -> None:
        """
        Set and save the user data directory.
        
        Args:
            path: The directory to use for user data
        """
        self._user_data_dir = path
        if self._is_frozen:
            self.save_user_data_location(path)
        
        # Ensure directories exist in the new location
        self.ensure_directories_exist()
    
    def ensure_directories_exist(self) -> dict:
        """
        Ensure all required user data directories exist.
        
        Returns:
            dict: Dictionary with paths to all user directories
        """
        user_data_dir = self.get_user_data_dir()
        
        directories = {
            'base': user_data_dir,
            'front': user_data_dir / 'front',
            'back': user_data_dir / 'back',
            'double_sided': user_data_dir / 'double_sided',
            'output': user_data_dir / 'output',
            'decklist': user_data_dir / 'decklist',
        }
        
        # Create all directories
        for dir_path in directories.values():
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Create EMPTY.md placeholder if directory is empty
            if dir_path.name in ['front', 'back', 'double_sided']:
                readme_file = dir_path / 'EMPTY.md'
                if not readme_file.exists():
                    readme_file.write_text(
                        f"# {dir_path.name.replace('_', ' ').title()} Directory\n\n"
                        f"Place your card images here.\n"
                    )
        
        return {k: str(v) for k, v in directories.items()}
    
    def get_default_paths(self) -> dict:
        """
        Get default paths for all user data directories.
        
        Returns:
            dict: Dictionary with default paths
        """
        dirs = self.ensure_directories_exist()
        return {
            'front_dir': dirs['front'],
            'back_dir': dirs['back'],
            'double_sided_dir': dirs['double_sided'],
            'output_dir': dirs['output'],
            'decklist_dir': dirs['decklist'],
        }
    
    def is_first_run(self) -> bool:
        """
        Check if this is the first time the application is run.
        
        Returns:
            bool: True if this appears to be the first run
        """
        if not self._is_frozen:
            # Development mode - not first run
            return False
        
        # Check if user has configured their data directory
        return not self.is_configured()
    
    def is_packaged(self) -> bool:
        """
        Check if running as a packaged executable.
        
        Returns:
            bool: True if running as packaged executable
        """
        return self._is_frozen


# Global instance
_user_data_manager = UserDataManager()


def get_user_data_manager() -> UserDataManager:
    """Get the global UserDataManager instance."""
    return _user_data_manager
