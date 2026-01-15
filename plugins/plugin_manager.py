"""
Plugin Manager for Card Game Fetchers
Centralizes registration and management of different card game plugins
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Any
import importlib
import sys
import os


@dataclass
class GamePlugin:
    """Represents a card game plugin with its capabilities"""
    id: str  # Unique identifier (e.g., "mtg", "lorcana")
    name: str  # Display name (e.g., "Magic: The Gathering")
    deck_formats: List[str]  # Supported deck list formats
    fetch_module: str  # Python module path to the fetch function
    
    # Feature support flags
    supports_set_collector: bool = True
    supports_showcase: bool = False
    supports_extra_art: bool = False
    supports_older_sets: bool = False
    supports_tokens: bool = False
    supports_art_crop: bool = True
    supports_parallel: bool = True
    
    # Plugin-specific data
    metadata: Dict[str, Any] = field(default_factory=dict)


class PluginManager:
    """Manages registration and access to card game plugins"""
    
    def __init__(self):
        self.plugins: Dict[str, GamePlugin] = {}
        self._register_builtin_plugins()
    
    def _register_builtin_plugins(self):
        """Register all built-in game plugins"""
        
        # Magic: The Gathering
        self.register_plugin(GamePlugin(
            id="mtg",
            name="Magic: The Gathering",
            deck_formats=["archidekt", "moxfield", "deckstats", "tappedout", "mtga", "mtgo", "mpcfill_xml", "generic"],
            fetch_module="plugins.mtg.fetch",
            supports_set_collector=True,
            supports_showcase=True,
            supports_extra_art=True,
            supports_older_sets=True,
            supports_tokens=True,
            supports_art_crop=True,
            supports_parallel=True,
            metadata={
                "default_format": "archidekt",
                "api": "scryfall"
            }
        ))
        
        # Disney Lorcana
        self.register_plugin(GamePlugin(
            id="lorcana",
            name="Disney Lorcana",
            deck_formats=["dreamborn", "generic"],
            fetch_module="plugins.lorcana.fetch",
            supports_set_collector=False,
            supports_showcase=False,
            supports_extra_art=False,
            supports_older_sets=False,
            supports_tokens=False,
            supports_art_crop=False,
            supports_parallel=False,
            metadata={
                "default_format": "dreamborn",
                "api": "lorcast"
            }
        ))
        
        # Yu-Gi-Oh!
        self.register_plugin(GamePlugin(
            id="yugioh",
            name="Yu-Gi-Oh!",
            deck_formats=["ydk", "generic"],
            fetch_module="plugins.yugioh.fetch",
            supports_set_collector=False,
            supports_showcase=False,
            supports_extra_art=False,
            supports_older_sets=False,
            supports_tokens=False,
            supports_art_crop=False,
            supports_parallel=False,
            metadata={
                "default_format": "ydk",
                "api": "ygoprodeck"
            }
        ))
        
        # Star Wars Unlimited
        self.register_plugin(GamePlugin(
            id="star_wars_unlimited",
            name="Star Wars Unlimited",
            deck_formats=["swudb", "generic"],
            fetch_module="plugins.star_wars_unlimited.fetch",
            supports_set_collector=False,
            supports_showcase=False,
            supports_extra_art=False,
            supports_older_sets=False,
            supports_tokens=False,
            supports_art_crop=False,
            supports_parallel=False,
            metadata={
                "default_format": "swudb",
                "api": "swudb"
            }
        ))
        
        # One Piece
        self.register_plugin(GamePlugin(
            id="one_piece",
            name="One Piece Card Game",
            deck_formats=["onepiece_top", "generic"],
            fetch_module="plugins.one_piece.fetch",
            supports_set_collector=False,
            supports_showcase=False,
            supports_extra_art=False,
            supports_older_sets=False,
            supports_tokens=False,
            supports_art_crop=False,
            supports_parallel=False,
            metadata={
                "default_format": "onepiece_top",
                "api": "onepiece_top"
            }
        ))
        
        # Digimon
        self.register_plugin(GamePlugin(
            id="digimon",
            name="Digimon Card Game",
            deck_formats=["digimoncard", "generic"],
            fetch_module="plugins.digimon.fetch",
            supports_set_collector=False,
            supports_showcase=False,
            supports_extra_art=False,
            supports_older_sets=False,
            supports_tokens=False,
            supports_art_crop=False,
            supports_parallel=False,
            metadata={
                "default_format": "digimoncard",
                "api": "digimoncard"
            }
        ))
        
        # Flesh and Blood
        self.register_plugin(GamePlugin(
            id="flesh_and_blood",
            name="Flesh and Blood",
            deck_formats=["fabdb", "generic"],
            fetch_module="plugins.flesh_and_blood.fetch",
            supports_set_collector=False,
            supports_showcase=False,
            supports_extra_art=False,
            supports_older_sets=False,
            supports_tokens=False,
            supports_art_crop=False,
            supports_parallel=False,
            metadata={
                "default_format": "fabdb",
                "api": "fabdb"
            }
        ))
        
        # Grand Archive
        self.register_plugin(GamePlugin(
            id="grand_archive",
            name="Grand Archive TCG",
            deck_formats=["gatcg", "generic"],
            fetch_module="plugins.grand_archive.fetch",
            supports_set_collector=False,
            supports_showcase=False,
            supports_extra_art=False,
            supports_older_sets=False,
            supports_tokens=False,
            supports_art_crop=False,
            supports_parallel=False,
            metadata={
                "default_format": "gatcg",
                "api": "gatcg"
            }
        ))
        
        # Altered TCG
        self.register_plugin(GamePlugin(
            id="altered",
            name="Altered TCG",
            deck_formats=["ajordat", "generic"],
            fetch_module="plugins.altered.fetch",
            supports_set_collector=False,
            supports_showcase=False,
            supports_extra_art=False,
            supports_older_sets=False,
            supports_tokens=False,
            supports_art_crop=False,
            supports_parallel=False,
            metadata={
                "default_format": "ajordat",
                "api": "altered"
            }
        ))
        
        # Gundam Card Game
        self.register_plugin(GamePlugin(
            id="gundam",
            name="Gundam Card Game",
            deck_formats=["deckplanet", "limitless", "egman", "exburst", "generic"],
            fetch_module="plugins.gundam.fetch",
            supports_set_collector=False,
            supports_showcase=False,
            supports_extra_art=False,
            supports_older_sets=False,
            supports_tokens=False,
            supports_art_crop=False,
            supports_parallel=False,
            metadata={
                "default_format": "deckplanet",
                "api": "bandai"
            }
        ))
        
        # Android: Netrunner
        self.register_plugin(GamePlugin(
            id="netrunner",
            name="Android: Netrunner",
            deck_formats=["text", "bbcode", "markdown", "plain_text", "jinteki", "generic"],
            fetch_module="plugins.netrunner.fetch",
            supports_set_collector=False,
            supports_showcase=False,
            supports_extra_art=False,
            supports_older_sets=False,
            supports_tokens=False,
            supports_art_crop=False,
            supports_parallel=False,
            metadata={
                "default_format": "jinteki",
                "api": "netrunnerdb"
            }
        ))
        
        # Riftbound
        self.register_plugin(GamePlugin(
            id="riftbound",
            name="Riftbound",
            deck_formats=["tts", "pixelborn", "piltover_archive", "generic"],
            fetch_module="plugins.riftbound.fetch",
            supports_set_collector=False,
            supports_showcase=False,
            supports_extra_art=False,
            supports_older_sets=False,
            supports_tokens=False,
            supports_art_crop=False,
            supports_parallel=False,
            metadata={
                "default_format": "tts",
                "api": "riftbound"
            }
        ))
    
    def register_plugin(self, plugin: GamePlugin):
        """Register a game plugin"""
        self.plugins[plugin.id] = plugin
    
    def get_plugin(self, plugin_id: str) -> Optional[GamePlugin]:
        """Get a specific plugin by ID"""
        return self.plugins.get(plugin_id)
    
    def get_all_plugins(self) -> List[GamePlugin]:
        """Get all registered plugins sorted by name"""
        return sorted(self.plugins.values(), key=lambda p: p.name)
    
    def get_plugin_names(self) -> Dict[str, str]:
        """Get mapping of plugin IDs to display names"""
        return {p.id: p.name for p in self.plugins.values()}
    
    def get_formats_for_plugin(self, plugin_id: str) -> List[str]:
        """Get supported deck formats for a specific plugin"""
        plugin = self.get_plugin(plugin_id)
        return plugin.deck_formats if plugin else []


# Global plugin manager instance
_plugin_manager = None

def get_plugin_manager() -> PluginManager:
    """Get the global plugin manager instance"""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager
