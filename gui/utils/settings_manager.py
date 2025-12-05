"""
Settings Manager - Handles loading and saving GUI settings to JSON
"""
import json
import os


class SettingsManager:
    """Manages GUI settings persistence"""
    
    def __init__(self, settings_file):
        """
        Initialize settings manager
        
        Args:
            settings_file: Path to the JSON settings file
        """
        self.settings_file = settings_file
        # Ensure data directory exists
        os.makedirs(os.path.dirname(settings_file), exist_ok=True)
    
    def load_settings(self, variables):
        """
        Load saved settings from JSON file
        
        Args:
            variables: Dictionary mapping setting names to Tkinter variables
        """
        if not os.path.exists(self.settings_file):
            return
        
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # Load each setting into its corresponding variable
            for key, var in variables.items():
                if key in settings:
                    try:
                        var.set(settings[key])
                    except Exception as e:
                        print(f"Warning: Could not load setting '{key}': {e}")
                        
        except Exception as e:
            # If settings file is corrupted, just ignore and use defaults
            print(f"Warning: Could not load settings: {e}")
    
    def save_settings(self, variables):
        """
        Save current settings to JSON file
        
        Args:
            variables: Dictionary mapping setting names to Tkinter variables
        """
        try:
            settings = {}
            for key, var in variables.items():
                try:
                    settings[key] = var.get()
                except Exception as e:
                    print(f"Warning: Could not save setting '{key}': {e}")
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
                
        except Exception as e:
            print(f"Warning: Could not save settings: {e}")
