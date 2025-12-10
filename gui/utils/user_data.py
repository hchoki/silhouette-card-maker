"""
User Data Directory Management

Handles the location of user data directories.
ALWAYS uses local directories (game/, data/) whether running from source or as packaged exe.
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
        
    def get_application_root(self) -> Path:
        """
        Get the application root directory.
        - When packaged: directory where .exe is located
        - When running from source: repository root
        
        Returns:
            Path: The application root directory
        """
        if self._is_frozen:
            # Packaged executable - use exe directory
            return Path(sys.executable).parent
        else:
            # Development mode - use repository root
            return Path(__file__).parent.parent.parent
    
    def get_config_dir(self) -> Path:
        """
        Get the configuration directory path for settings and offset profiles.
        ALWAYS uses local 'data' directory in application root.
        
        Returns:
            Path: The configuration directory (always <app_root>/data)
        """
        config_dir = self.get_application_root() / 'data'
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    def get_default_root_suggestion(self) -> Path:
        """
        Get the suggested default root directory for game data.
        ALWAYS returns <app_root>/game
        
        Returns:
            Path: The game directory
        """
        return self.get_application_root() / 'game'
    
    def load_user_data_location(self) -> Optional[Path]:
        """
        Load the user-selected data directory from config.
        NOTE: For compatibility, but always returns game/ directory.
        
        Returns:
            Path: The game directory (always <app_root>/game)
        """
        return self.get_default_root_suggestion()
    
    def save_user_data_location(self, path: Path) -> None:
        """
        No-op: Data directory is always local, no need to save preference.
        
        Args:
            path: Ignored
        """
        pass
    
    def is_configured(self) -> bool:
        """
        Check if user has configured their data directory.
        Always returns True since we always use local game/ directory.
        
        Returns:
            bool: Always True
        """
        return True
        
    def get_user_data_dir(self) -> Path:
        """
        Get the user data directory path.
        ALWAYS returns <app_root>/game whether packaged or running from source.
        
        Returns:
            Path: The game directory
        """
        return self.get_application_root() / 'game'
    
    def set_user_data_dir(self, path: Path) -> None:
        """
        No-op: Data directory is always local game/, cannot be changed.
        
        Args:
            path: Ignored
        """
        pass
    
    def ensure_directories_exist(self) -> dict:
        """
        Ensure all required user data directories exist.
        
        Returns:
            dict: Dictionary with paths to all user directories
        """
        user_data_dir = self.get_user_data_dir()
        
        directories = {
            'base': user_data_dir,
            'game': user_data_dir,
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
        Always returns False since we don't need first-run setup.
        
        Returns:
            bool: Always False
        """
        return False
    
    def is_packaged(self) -> bool:
        """
        Check if running as a packaged executable.
        
        Returns:
            bool: True if running as packaged executable
        """
        return self._is_frozen
    
    def ensure_user_data_structure(self) -> None:
        """
        Ensure the complete user data structure exists.
        Creates all necessary directories.
        """
        self.ensure_directories_exist()


# Global instance
_user_data_manager = UserDataManager()


def get_user_data_manager() -> UserDataManager:
    """Get the global UserDataManager instance."""
    return _user_data_manager
