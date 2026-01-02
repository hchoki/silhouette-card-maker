"""
Card Fetcher & PDF Creator - Graphical User Interface

A GUI for fetching card game cards and creating PDFs without using the command line.
Supports multiple card games through a plugin system.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from pathlib import Path
import queue

# Add plugins to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'plugins'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'plugins', 'mtg'))

# Import GUI utilities
from gui.utils.settings_manager import SettingsManager
from gui.utils.styles import StyleManager
from gui.utils.user_data import get_user_data_manager

# Import plugin manager
from plugins.plugin_manager import get_plugin_manager

# Import MTG-specific modules (for backward compatibility)
from deck_formats import DeckFormat
from scryfall import get_handle_card as scryfall_get_handle_card
from deck_formats import parse_deck
from utilities import (
    Registration, CardSize, PaperSize, generate_pdf,
    load_saved_offset, save_offset,
    load_offset_profiles, load_offset_profile, save_offset_profile,
    list_offset_profiles, delete_offset_profile, set_default_offset_profile
)


class MTGCardFetcherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Card Fetcher & PDF Creator")
        self.root.geometry("1400x950")
        self.root.minsize(1200, 850)
        
        # Message queue for thread-safe GUI updates
        self.message_queue = queue.Queue()
        
        # Configure modern style using StyleManager
        StyleManager.setup_styles(root)
        
        # Initialize plugin manager
        self.plugin_manager = get_plugin_manager()
        
        # Initialize user data manager (uses local directories even when packaged)
        self.user_data_manager = get_user_data_manager()
        self.user_data_manager.ensure_user_data_structure()
        
        # Fetch card variables
        self.selected_game = tk.StringVar(value="mtg")  # Default to MTG
        self.deck_path = tk.StringVar()
        self.temp_deck_file = None  # Temporary file for pasted text
        self.deck_format = tk.StringVar(value="archidekt")
        self.art_crop = tk.BooleanVar(value=False)
        self.tokens = tk.BooleanVar(value=False)
        self.parallel = tk.BooleanVar(value=True)
        self.max_workers = tk.IntVar(value=6)
        self.api_delay = tk.DoubleVar(value=0.05)
        self.prefer_showcase = tk.BooleanVar(value=False)
        self.prefer_extra_art = tk.BooleanVar(value=False)
        self.prefer_older_sets = tk.BooleanVar(value=False)
        self.ignore_set_collector = tk.BooleanVar(value=False)
        
        # Get default paths from user data manager
        default_paths = self.user_data_manager.get_default_paths()
        self.default_front_dir = default_paths['front_dir']
        self.default_back_dir = default_paths['back_dir']
        self.default_double_sided_dir = default_paths['double_sided_dir']
        self.default_output_dir = default_paths['output_dir']
        
        # PDF creation variables
        self.front_dir = tk.StringVar(value=default_paths['front_dir'])
        self.back_dir = tk.StringVar(value=default_paths['back_dir'])
        self.selected_back_card = tk.StringVar(value="")
        self.double_sided_dir = tk.StringVar(value=default_paths['double_sided_dir'])
        self.output_pdf_path = tk.StringVar(value=os.path.join(default_paths['output_dir'], 'game.pdf'))
        self.card_size = tk.StringVar(value=CardSize.STANDARD.value)
        self.paper_size = tk.StringVar(value=PaperSize.LETTER.value)
        self.registration = tk.StringVar(value=Registration.THREE.value)
        self.only_fronts = tk.BooleanVar(value=False)
        self.output_images = tk.BooleanVar(value=False)
        self.crop_amount = tk.StringVar(value="")
        self.extend_corners = tk.IntVar(value=0)
        self.ppi = tk.IntVar(value=300)
        self.pdf_quality = tk.IntVar(value=75)
        self.pdf_name = tk.StringVar(value="")
        
        # Offset variables
        self.x_offset = tk.IntVar(value=0)
        self.y_offset = tk.IntVar(value=0)
        self.angle_offset = tk.DoubleVar(value=0.0)
        self.selected_profile = tk.StringVar(value="")
        self.pdf_selected_profile = tk.StringVar(value="")  # For Create PDF tab
        self.profile_name = tk.StringVar(value="")
        self.profile_description = tk.StringVar(value="")
        self.profile_paper_size = tk.StringVar(value=PaperSize.LETTER.value)
        
        self.is_fetching = False
        self.is_creating_pdf = False
        self.last_created_pdf = None  # Track the last created PDF for "Open" button
        self.cancel_fetch = False  # Flag to cancel fetch operation
        self.total_cards = 0
        self.completed_cards = 0
        self.is_initializing = True  # Flag to prevent callbacks during setup
        
        # Initialize settings manager using config directory
        settings_file = os.path.join(self.user_data_manager.get_config_dir(), 'gui_settings.json')
        self.settings_manager = SettingsManager(settings_file)
        
        # Load saved settings
        self.load_settings()
        self.setup_ui()
        self.check_message_queue()
        
        # Initialize back card list after UI setup
        self.root.after(100, self.update_back_card_list)
        
        # Mark initialization as complete
        self.is_initializing = False
        
        # Save settings on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    # ============================================================================
    # SETTINGS MANAGEMENT
    # ============================================================================
    
    def _get_settings_variables(self):
        """Get dictionary of all settings variables for persistence"""
        return {
            # Fetch tab settings
            'selected_game': self.selected_game,
            'deck_format': self.deck_format,
            'art_crop': self.art_crop,
            'tokens': self.tokens,
            'parallel': self.parallel,
            'max_workers': self.max_workers,
            'api_delay': self.api_delay,
            'prefer_showcase': self.prefer_showcase,
            'prefer_extra_art': self.prefer_extra_art,
            'prefer_older_sets': self.prefer_older_sets,
            'ignore_set_collector': self.ignore_set_collector,
            
            # PDF tab settings
            'front_dir': self.front_dir,
            'back_dir': self.back_dir,
            'selected_back_card': self.selected_back_card,
            'double_sided_dir': self.double_sided_dir,
            'output_pdf_path': self.output_pdf_path,
            'card_size': self.card_size,
            'paper_size': self.paper_size,
            'registration': self.registration,
            'only_fronts': self.only_fronts,
            'output_images': self.output_images,
            'crop_amount': self.crop_amount,
            'extend_corners': self.extend_corners,
            'ppi': self.ppi,
            'pdf_quality': self.pdf_quality,
            'pdf_selected_profile': self.pdf_selected_profile,
            
            # Offset tab settings
            'x_offset': self.x_offset,
            'y_offset': self.y_offset,
            'angle_offset': self.angle_offset,
            'profile_paper_size': self.profile_paper_size,
        }
    
    def load_settings(self):
        """Load saved settings from JSON file"""
        self.settings_manager.load_settings(self._get_settings_variables())
    
    def save_settings(self):
        """Save current settings to JSON file"""
        self.settings_manager.save_settings(self._get_settings_variables())
    
    def on_closing(self):
        """Handle window closing"""
        self.save_settings()
        self.cleanup_temp_deck_file()
        self.root.destroy()
    
    # ============================================================================
    # UI SETUP
    # ============================================================================
    
    def setup_ui(self):
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20", style='TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(main_frame, style='TNotebook')
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        
        # Tab 1: Fetch Cards
        fetch_tab = ttk.Frame(self.notebook, style='TFrame', padding="10")
        fetch_tab.columnconfigure(0, weight=1, uniform='columns')
        fetch_tab.columnconfigure(1, weight=1, uniform='columns')
        fetch_tab.rowconfigure(0, weight=1)
        self.notebook.add(fetch_tab, text='  📥 Fetch Cards  ')
        self.setup_fetch_tab(fetch_tab)
        
        # Tab 2: Create PDF
        pdf_tab = ttk.Frame(self.notebook, style='TFrame', padding="10")
        pdf_tab.columnconfigure(0, weight=1, uniform='columns')
        pdf_tab.columnconfigure(1, weight=1, uniform='columns')
        pdf_tab.rowconfigure(0, weight=1)
        self.notebook.add(pdf_tab, text='  📄 Create PDF  ')
        self.setup_pdf_tab(pdf_tab)
        
        # Tab 3: Offset PDF
        offset_tab = ttk.Frame(self.notebook, style='TFrame', padding="10")
        offset_tab.columnconfigure(0, weight=1, uniform='columns')
        offset_tab.columnconfigure(1, weight=1, uniform='columns')
        offset_tab.rowconfigure(0, weight=1)
        self.notebook.add(offset_tab, text='  ⚙️ Offset PDF  ')
        self.setup_offset_tab(offset_tab)
        
        # Initialize game-specific UI state after all tabs are setup
        self.on_game_changed()
    
    def setup_fetch_tab(self, parent):
        """Setup the card fetching tab"""
        # Left column - Settings (with scrollbar)
        left_container = ttk.Frame(parent, style='TFrame')
        left_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 2))
        left_container.rowconfigure(0, weight=1)
        left_container.columnconfigure(0, weight=1)
        
        # Canvas for scrolling
        canvas = tk.Canvas(left_container, bg='#1e1e1e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(left_container, orient='vertical', command=canvas.yview)
        left_frame = ttk.Frame(canvas, style='TFrame')
        
        def on_fetch_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
            # Show/hide scrollbar based on content size
            canvas_height = canvas.winfo_height()
            if canvas.bbox('all') and canvas_height > 1:  # Ensure canvas is rendered
                if canvas.bbox('all')[3] <= canvas_height:
                    scrollbar.grid_remove()
                else:
                    scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        left_frame.bind('<Configure>', on_fetch_frame_configure)
        canvas.bind('<Configure>', lambda e: on_fetch_frame_configure(e))  # Also check on canvas resize
        
        canvas.create_window((0, 0), window=left_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar.grid_remove()  # Hide initially
        
        # Force initial check after a short delay to ensure window is rendered
        self.root.after(100, lambda: on_fetch_frame_configure(None))
        
        # Game selection
        game_frame = ttk.LabelFrame(left_frame, text="  🎮 Card Game  ", padding="8", style='TLabelframe')
        game_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=5)
        game_frame.columnconfigure(1, weight=1)
        
        ttk.Label(game_frame, text="Select Game:", style='Card.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        # Get all available games from plugin manager
        game_names = [(p.name, p.id) for p in self.plugin_manager.get_all_plugins()]
        
        # Create a mapping for display
        self.game_id_to_name = {gid: name for name, gid in game_names}
        self.game_name_to_id = {name: gid for name, gid in game_names}
        
        # Use display names in combobox
        display_names = [name for name, _ in game_names]
        
        self.game_combo = ttk.Combobox(game_frame, 
                                       values=display_names,
                                       state='readonly', width=30, style='TCombobox')
        self.game_combo.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Set initial value to MTG's display name (before binding to avoid triggering callback)
        initial_game_id = self.selected_game.get()
        if initial_game_id in self.game_id_to_name:
            self.game_combo.set(self.game_id_to_name[initial_game_id])
        
        # Deck file selection
        deck_frame = ttk.LabelFrame(left_frame, text="  📂 Deck File  ", padding="8", style='TLabelframe')
        deck_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=5)
        deck_frame.columnconfigure(1, weight=1)
        
        deck_label = ttk.Label(deck_frame, text="Deck List:", style='Card.TLabel')
        deck_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        deck_entry = ttk.Entry(deck_frame, textvariable=self.deck_path, width=40, style='TEntry')
        deck_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Button container for Browse and Paste Text
        btn_frame = ttk.Frame(deck_frame, style='TFrame')
        btn_frame.grid(row=0, column=2)
        
        browse_btn = ttk.Button(btn_frame, text="Browse...", style='TButton')
        browse_btn.configure(command=self.browse_deck)
        browse_btn.grid(row=0, column=0, padx=(0, 5))
        
        paste_btn = ttk.Button(btn_frame, text="Paste Text...", style='TButton')
        paste_btn.configure(command=self.paste_decklist_text)
        paste_btn.grid(row=0, column=1)
        
        format_label = ttk.Label(deck_frame, text="Format:", style='Card.TLabel')
        format_label.grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.format_combo = ttk.Combobox(deck_frame, textvariable=self.deck_format, 
                                     values=['archidekt', 'moxfield', 'deckstats', 'tappedout', 'generic'], 
                                     state='readonly', width=20, style='TCombobox')
        self.format_combo.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        # Basic options
        self.basic_frame = ttk.LabelFrame(left_frame, text="  ⚙️ Basic Options  ", padding="8", style='TLabelframe')
        self.basic_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=5)
        
        self.art_crop_check = ttk.Checkbutton(self.basic_frame, text="Download Art Crop (for Proxyshop)", 
                        variable=self.art_crop)
        self.tokens_check = ttk.Checkbutton(self.basic_frame, text="Fetch Related Tokens", 
                        variable=self.tokens)
        self.ignore_set_check = ttk.Checkbutton(self.basic_frame, text="Ignore Set & Collector Number", 
                        variable=self.ignore_set_collector)
        
        # Card preferences
        self.pref_frame = ttk.LabelFrame(left_frame, text="  🎨 Card Preferences  ", padding="8", style='TLabelframe')
        self.pref_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=5)
        
        self.showcase_check = ttk.Checkbutton(self.pref_frame, text="Prefer Showcase Cards", 
                        variable=self.prefer_showcase)
        self.extra_art_check = ttk.Checkbutton(self.pref_frame, text="Prefer Full Art / Borderless / Extended Art", 
                        variable=self.prefer_extra_art)
        self.older_sets_check = ttk.Checkbutton(self.pref_frame, text="Prefer Older Sets", 
                        variable=self.prefer_older_sets)
        
        # Performance options
        self.perf_frame = ttk.LabelFrame(left_frame, text="  🚀 Performance Settings  ", padding="8", style='TLabelframe')
        self.perf_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=5)
        
        self.parallel_check = ttk.Checkbutton(self.perf_frame, text="Enable Parallel Downloads", 
                        variable=self.parallel, command=self.toggle_parallel)
        self.parallel_check.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Initialize formats for the selected game (without overwriting loaded deck_format)
        # Must be called after all option checkboxes are created
        self.update_game_formats(preserve_format=True)
        
        ttk.Label(self.perf_frame, text="Max Workers:", style='Card.TLabel').grid(row=1, column=0, sticky=tk.W, padx=(20, 10), pady=5)
        self.workers_spinbox = ttk.Spinbox(self.perf_frame, from_=1, to=20, textvariable=self.max_workers, 
                                          width=10, style='TSpinbox')
        self.workers_spinbox.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self.perf_frame, text="API Delay (seconds):", style='Card.TLabel').grid(row=2, column=0, sticky=tk.W, padx=(20, 10), pady=5)
        delay_spinbox = ttk.Spinbox(self.perf_frame, from_=0.01, to=0.5, increment=0.01, 
                                     textvariable=self.api_delay, width=10, format="%.2f", style='TSpinbox')
        delay_spinbox.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self.perf_frame, text="(Lower = faster, but respect Scryfall's limits)", 
                  font=('Segoe UI', 8), foreground='#808080', style='Card.TLabel').grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=(20, 0))
        
        # Button frame
        button_frame = ttk.Frame(left_frame, style='TFrame')
        button_frame.grid(row=5, column=0, pady=(8, 8), padx=5)
        
        # Fetch button (will toggle to Cancel during fetching)
        self.fetch_btn = ttk.Button(button_frame, text="🚀 Start Fetching Cards", 
                                     command=self.toggle_fetch, style='Accent.TButton', width=22)
        self.fetch_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Cleanup button
        self.cleanup_btn = ttk.Button(button_frame, text="🧹 Cleanup Images",
                                      command=self.cleanup_images, style='Secondary.TButton', width=22)
        self.cleanup_btn.pack(side=tk.LEFT)
        
        # Right column - Progress
        right_frame = ttk.Frame(parent, style='TFrame')
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        
        # Progress section
        progress_frame = ttk.LabelFrame(right_frame, text="  📊 Progress  ", padding="12", style='TLabelframe')
        progress_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(0, weight=1)
        
        # Log text area with custom styling
        log_container = ttk.Frame(progress_frame, style='TFrame')
        log_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_container.columnconfigure(0, weight=1)
        log_container.rowconfigure(0, weight=1)
        
        # Create scrollbar that only shows when needed
        progress_scrollbar = ttk.Scrollbar(log_container, orient='vertical')
        
        self.progress_text = tk.Text(log_container, height=25, 
                                     state='disabled', wrap=tk.WORD,
                                     bg='#1e1e1e', fg='#d4d4d4',
                                     font=('Consolas', 9),
                                     relief='solid', borderwidth=1,
                                     padx=10, pady=10,
                                     insertbackground='#d4d4d4',
                                     yscrollcommand=progress_scrollbar.set)
        progress_scrollbar.config(command=self.progress_text.yview)
        
        self.progress_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        progress_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        progress_scrollbar.grid_remove()  # Hide initially
        
        # Auto-hide scrollbar when not needed
        def _progress_scrollbar_autohide(*args):
            progress_scrollbar.set(*args)
            if float(args[0]) == 0.0 and float(args[1]) == 1.0:
                progress_scrollbar.grid_remove()
            else:
                progress_scrollbar.grid()
        self.progress_text.config(yscrollcommand=_progress_scrollbar_autohide)
        
        # Configure text tags for colored output
        self.progress_text.tag_config('success', foreground='#4ec9b0')
        self.progress_text.tag_config('error', foreground='#f48771')
        self.progress_text.tag_config('info', foreground='#9cdcfe')
        self.progress_text.tag_config('warning', foreground='#dcdcaa')
        self.progress_text.tag_config('card', foreground='#4ec9b0', font=('Consolas', 9, 'bold'))
        
        # Bind game change event AFTER all widgets are created and formats are initialized
        # This prevents the callback from firing during initial setup
        self.game_combo.bind('<<ComboboxSelected>>', self.on_game_changed)
    
    def toggle_parallel(self):
        """Enable/disable parallel-related options based on checkbox"""
        state = 'normal' if self.parallel.get() else 'disabled'
        self.workers_spinbox.configure(state=state)
    
    def on_game_changed(self, event=None):
        """Update available formats and options when game selection changes"""
        # Skip if we're still initializing the UI
        if self.is_initializing:
            return
        
        # Get selected game name from combobox display
        game_display = self.game_combo.get()
        
        # Convert display name to ID
        game_id = self.game_name_to_id.get(game_display)
        if not game_id:
            return
        
        # Update the internal game ID variable
        self.selected_game.set(game_id)
        
        # Update formats (will reset to default since user manually changed game)
        self.update_game_formats(preserve_format=False)
    
    def update_game_formats(self, preserve_format=False):
        """Update available deck formats based on selected game"""
        game_id = self.selected_game.get()
        plugin = self.plugin_manager.get_plugin(game_id)
        if not plugin:
            return
        
        # Save current format if we want to preserve it
        current_format = self.deck_format.get() if preserve_format else None
        
        # Update available formats
        self.format_combo['values'] = plugin.deck_formats
        
        # Set format: preserve current if valid, otherwise use default
        if current_format and current_format in plugin.deck_formats:
            self.deck_format.set(current_format)
        elif plugin.deck_formats:
            default_format = plugin.metadata.get('default_format', plugin.deck_formats[0])
            self.deck_format.set(default_format)
        
        # Hide/show options based on plugin support
        # First, forget all option widgets
        self.art_crop_check.grid_forget()
        self.tokens_check.grid_forget()
        self.ignore_set_check.grid_forget()
        self.showcase_check.grid_forget()
        self.extra_art_check.grid_forget()
        self.older_sets_check.grid_forget()
        self.parallel_check.grid_forget()
        
        # Show and layout basic options that are supported
        basic_row = 0
        if plugin.supports_art_crop:
            self.art_crop_check.grid(row=basic_row, column=0, sticky=tk.W, pady=2)
            basic_row += 1
        if plugin.supports_tokens:
            self.tokens_check.grid(row=basic_row, column=0, sticky=tk.W, pady=2)
            basic_row += 1
        if plugin.supports_set_collector:
            self.ignore_set_check.grid(row=basic_row, column=0, sticky=tk.W, pady=2)
            basic_row += 1
        
        # Show and layout card preference options that are supported
        pref_row = 0
        if plugin.supports_showcase:
            self.showcase_check.grid(row=pref_row, column=0, sticky=tk.W, pady=2)
            pref_row += 1
        if plugin.supports_extra_art:
            self.extra_art_check.grid(row=pref_row, column=0, sticky=tk.W, pady=2)
            pref_row += 1
        if plugin.supports_older_sets:
            self.older_sets_check.grid(row=pref_row, column=0, sticky=tk.W, pady=2)
            pref_row += 1
        
        # Show parallel downloads if supported
        if plugin.supports_parallel:
            self.parallel_check.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Hide empty frames
        if basic_row == 0:
            self.basic_frame.grid_forget()
        else:
            self.basic_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=5)
        
        if pref_row == 0:
            self.pref_frame.grid_forget()
        else:
            self.pref_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=5)
        
        if not plugin.supports_parallel:
            self.perf_frame.grid_forget()
        else:
            self.perf_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=5)
    
    def toggle_offset_info(self):
        """Toggle visibility of the offset information section"""
        if self.info_visible.get():
            # Hide the info frame
            self.info_frame.grid_remove()
            self.info_toggle_btn.configure(text="▶ Show Information")
            self.info_visible.set(False)
        else:
            # Show the info frame
            self.info_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=5)
            self.info_toggle_btn.configure(text="▼ Hide Information")
            self.info_visible.set(True)
    
    def setup_pdf_tab(self, parent):
        """Setup the PDF creation tab"""
        # Left column - Settings (with scrollbar)
        left_container = ttk.Frame(parent, style='TFrame')
        left_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 2))
        left_container.rowconfigure(0, weight=1)
        left_container.columnconfigure(0, weight=1)
        
        # Canvas for scrolling
        canvas = tk.Canvas(left_container, bg='#1e1e1e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(left_container, orient='vertical', command=canvas.yview)
        left_frame = ttk.Frame(canvas, style='TFrame')
        
        def on_pdf_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
            # Show/hide scrollbar based on content size
            canvas_height = canvas.winfo_height()
            if canvas.bbox('all') and canvas_height > 1:  # Ensure canvas is rendered
                if canvas.bbox('all')[3] <= canvas_height:
                    scrollbar.grid_remove()
                else:
                    scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        left_frame.bind('<Configure>', on_pdf_frame_configure)
        canvas.bind('<Configure>', lambda e: on_pdf_frame_configure(e))  # Also check on canvas resize
        
        canvas.create_window((0, 0), window=left_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar.grid_remove()  # Hide initially
        
        # Force initial check after a short delay to ensure window is rendered
        self.root.after(100, lambda: on_pdf_frame_configure(None))
        
        # Directory paths
        paths_frame = ttk.LabelFrame(left_frame, text="  📁 Directories  ", padding="8", style='TLabelframe')
        paths_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=5)
        paths_frame.columnconfigure(1, weight=1)
        
        # Front directory
        ttk.Label(paths_frame, text="Front Cards:", style='Card.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Entry(paths_frame, textvariable=self.front_dir, style='TEntry').grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=5)
        ttk.Button(paths_frame, text="Browse...", command=lambda: self.browse_directory(self.front_dir), style='TButton').grid(row=0, column=2, pady=5)
        ttk.Button(paths_frame, text="↺", command=lambda: self.reset_directory(self.front_dir, self.default_front_dir), 
                  width=2, style='TButton').grid(row=0, column=3, pady=5, padx=(5, 0))
        
        # Back directory
        ttk.Label(paths_frame, text="Back Cards:", style='Card.TLabel').grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Entry(paths_frame, textvariable=self.back_dir, style='TEntry').grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=5)
        ttk.Button(paths_frame, text="Browse...", command=lambda: self.browse_directory(self.back_dir), style='TButton').grid(row=1, column=2, pady=5)
        ttk.Button(paths_frame, text="↺", command=lambda: self.reset_directory(self.back_dir, self.default_back_dir), 
                  width=2, style='TButton').grid(row=1, column=3, pady=5, padx=(5, 0))
        
        # Back card selector (for when multiple backs exist)
        ttk.Label(paths_frame, text="Select Back:", style='Card.TLabel').grid(row=1, column=4, sticky=tk.W, padx=(10, 10), pady=5)
        self.back_card_combo = ttk.Combobox(paths_frame, textvariable=self.selected_back_card, 
                                            state='readonly', style='TCombobox', width=20)
        self.back_card_combo.grid(row=1, column=5, sticky=tk.W, pady=5, padx=(0, 5))
        self.back_card_combo.set("(Auto-detect)")
        # Add refresh button with better styling
        refresh_btn = ttk.Button(paths_frame, text="↻", command=self.update_back_card_list, 
                                width=2, style='TButton')
        refresh_btn.grid(row=1, column=6, pady=5)
        # Bind back_dir changes to update the dropdown
        self.back_dir.trace_add('write', lambda *args: self.update_back_card_list())
        
        # Double-sided directory
        ttk.Label(paths_frame, text="Double-Sided:", style='Card.TLabel').grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Entry(paths_frame, textvariable=self.double_sided_dir, style='TEntry').grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=5)
        ttk.Button(paths_frame, text="Browse...", command=lambda: self.browse_directory(self.double_sided_dir), style='TButton').grid(row=2, column=2, pady=5)
        ttk.Button(paths_frame, text="↺", command=lambda: self.reset_directory(self.double_sided_dir, self.default_double_sided_dir), 
                  width=2, style='TButton').grid(row=2, column=3, pady=5, padx=(5, 0))
        
        # Output path
        ttk.Label(paths_frame, text="Output PDF:", style='Card.TLabel').grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Entry(paths_frame, textvariable=self.output_pdf_path, style='TEntry').grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=5)
        ttk.Button(paths_frame, text="Save As...", command=self.browse_pdf_output, style='TButton').grid(row=3, column=2, pady=5)
        
        # Quick access button (always show since we always use local directories)
        button_frame = ttk.Frame(paths_frame, style='TFrame')
        button_frame.grid(row=4, column=0, columnspan=3, pady=(10, 0))
        ttk.Button(button_frame, text="📂 Open Data Folder", 
                  command=self.open_user_data_folder, 
                  style='TButton').pack()
        
        # Card & Paper sizes
        size_frame = ttk.LabelFrame(left_frame, text="  📏 Size Settings  ", padding="8", style='TLabelframe')
        size_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=5)
        size_frame.columnconfigure(1, weight=1)
        
        ttk.Label(size_frame, text="Card Size:", style='Card.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Combobox(size_frame, textvariable=self.card_size, 
                    values=[s.value for s in CardSize], 
                    state='readonly', width=20, style='TCombobox').grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(size_frame, text="Paper Size:", style='Card.TLabel').grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Combobox(size_frame, textvariable=self.paper_size, 
                    values=[s.value for s in PaperSize], 
                    state='readonly', width=20, style='TCombobox').grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(size_frame, text="Registration:", style='Card.TLabel').grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Combobox(size_frame, textvariable=self.registration, 
                    values=[r.value for r in Registration], 
                    state='readonly', width=20, style='TCombobox').grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # PDF Options
        options_frame = ttk.LabelFrame(left_frame, text="  ⚙️ PDF Options  ", padding="8", style='TLabelframe')
        options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=5)
        options_frame.columnconfigure(1, weight=1)
        
        ttk.Checkbutton(options_frame, text="Only Fronts (exclude backs)", 
                       variable=self.only_fronts).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        ttk.Checkbutton(options_frame, text="Output as Images (instead of PDF)", 
                       variable=self.output_images).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Offset Profile Selection
        ttk.Label(options_frame, text="Apply Offset Profile:", style='Card.TLabel').grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.pdf_profile_combo = ttk.Combobox(options_frame, textvariable=self.pdf_selected_profile, 
                                              state='readonly', style='TCombobox', width=30)
        self.pdf_profile_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        self.pdf_profile_combo.bind('<<ComboboxSelected>>', self.update_pdf_profile_info)
        
        # Add "None" option, legacy offset, and populate profiles
        profile_list = ["(None - No Offset)"]
        
        # Check if legacy offset exists
        legacy_offset = load_saved_offset()
        if legacy_offset:
            profile_list.append("(Legacy Saved Offset)")
        
        profile_list.extend(list_offset_profiles())
        self.pdf_profile_combo['values'] = profile_list
        
        # Only set default profile if no saved setting was loaded
        if not self.pdf_selected_profile.get() or self.pdf_selected_profile.get() not in profile_list:
            profiles = load_offset_profiles()
            if profiles.default_profile and profiles.default_profile in profiles.profiles:
                self.pdf_selected_profile.set(profiles.default_profile)
            else:
                self.pdf_selected_profile.set("(None - No Offset)")
        
        # Profile info display
        self.pdf_profile_info_label = ttk.Label(options_frame, text="No offset will be applied", 
                                                style='Card.TLabel', font=('Segoe UI', 9), 
                                                foreground='#808080')
        self.pdf_profile_info_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(2, 10))
        self.update_pdf_profile_info()
        
        ttk.Label(options_frame, text="PDF Name Label:", style='Card.TLabel').grid(row=4, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Entry(options_frame, textvariable=self.pdf_name, width=30, style='TEntry').grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Advanced options
        advanced_frame = ttk.LabelFrame(left_frame, text="  🔧 Advanced  ", padding="8", style='TLabelframe')
        advanced_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=5)
        advanced_frame.columnconfigure(1, weight=1)
        
        ttk.Label(advanced_frame, text="Crop Amount:", style='Card.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Entry(advanced_frame, textvariable=self.crop_amount, width=15, style='TEntry').grid(row=0, column=1, sticky=tk.W, pady=5)
        ttk.Label(advanced_frame, text="(e.g., 3mm, 0.125in, 6.5)", 
                 font=('Segoe UI', 8), foreground='#808080', style='Card.TLabel').grid(row=1, column=0, columnspan=2, sticky=tk.W)
        
        ttk.Label(advanced_frame, text="Extend Corners:", style='Card.TLabel').grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Spinbox(advanced_frame, from_=0, to=100, textvariable=self.extend_corners, 
                   width=10, style='TSpinbox').grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(advanced_frame, text="PPI (Resolution):", style='Card.TLabel').grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Spinbox(advanced_frame, from_=72, to=600, textvariable=self.ppi, 
                   width=10, style='TSpinbox').grid(row=3, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(advanced_frame, text="Quality (0-100):", style='Card.TLabel').grid(row=4, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Spinbox(advanced_frame, from_=1, to=100, textvariable=self.pdf_quality, 
                   width=10, style='TSpinbox').grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Create button
        button_frame = ttk.Frame(left_frame, style='TFrame')
        button_frame.grid(row=4, column=0, pady=(8, 8), padx=5)
        
        self.create_pdf_btn = ttk.Button(button_frame, text="📄 Create PDF", 
                                        command=self.start_create_pdf, style='Accent.TButton')
        self.create_pdf_btn.pack(pady=5, ipadx=30, ipady=5)
        
        # Right column - Progress
        right_frame = ttk.Frame(parent, style='TFrame')
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        
        # Progress area
        progress_frame = ttk.LabelFrame(right_frame, text="  📊 Progress  ", padding="12", style='TLabelframe')
        progress_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(0, weight=1)
        
        # Log container to handle expansion properly
        log_container = ttk.Frame(progress_frame, style='TFrame')
        log_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_container.columnconfigure(0, weight=1)
        log_container.rowconfigure(0, weight=1)
        
        # Create scrollbar that only shows when needed
        pdf_progress_scrollbar = ttk.Scrollbar(log_container, orient='vertical')
        
        self.pdf_progress_text = tk.Text(log_container, 
                                         state='disabled', wrap=tk.WORD,
                                         bg='#1e1e1e', fg='#d4d4d4',
                                         font=('Consolas', 9),
                                         relief='solid', borderwidth=1,
                                         padx=10, pady=10,
                                         yscrollcommand=pdf_progress_scrollbar.set)
        pdf_progress_scrollbar.config(command=self.pdf_progress_text.yview)
        
        self.pdf_progress_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        pdf_progress_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        pdf_progress_scrollbar.grid_remove()  # Hide initially
        
        # Auto-hide scrollbar when not needed
        def _pdf_scrollbar_autohide(*args):
            pdf_progress_scrollbar.set(*args)
            if float(args[0]) == 0.0 and float(args[1]) == 1.0:
                pdf_progress_scrollbar.grid_remove()
            else:
                pdf_progress_scrollbar.grid()
        self.pdf_progress_text.config(yscrollcommand=_pdf_scrollbar_autohide)
        
        # Configure text tags
        self.pdf_progress_text.tag_config('success', foreground='#4ec9b0')
        self.pdf_progress_text.tag_config('error', foreground='#f48771')
        self.pdf_progress_text.tag_config('info', foreground='#9cdcfe')
    
    def setup_offset_tab(self, parent):
        """Setup the PDF offset tab with profile management"""
        # Left column - Settings (with scrollbar)
        left_container = ttk.Frame(parent, style='TFrame')
        left_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 2))
        left_container.rowconfigure(0, weight=1)
        left_container.columnconfigure(0, weight=1)
        
        # Canvas for scrolling
        canvas = tk.Canvas(left_container, bg='#1e1e1e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(left_container, orient='vertical', command=canvas.yview)
        left_frame = ttk.Frame(canvas, style='TFrame')
        
        def on_offset_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
            # Show/hide scrollbar based on content size
            canvas_height = canvas.winfo_height()
            if canvas.bbox('all') and canvas_height > 1:  # Ensure canvas is rendered
                if canvas.bbox('all')[3] <= canvas_height:
                    scrollbar.grid_remove()
                else:
                    scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        left_frame.bind('<Configure>', on_offset_frame_configure)
        canvas.bind('<Configure>', lambda e: on_offset_frame_configure(e))  # Also check on canvas resize
        
        canvas.create_window((0, 0), window=left_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar.grid_remove()  # Hide initially
        
        # Force initial check after a short delay to ensure window is rendered
        self.root.after(100, lambda: on_offset_frame_configure(None))
        
        # Load saved offset or default profile on startup
        profiles = load_offset_profiles()
        if profiles.default_profile and profiles.default_profile in profiles.profiles:
            default_prof = profiles.profiles[profiles.default_profile]
            self.x_offset.set(default_prof.x_offset)
            self.y_offset.set(default_prof.y_offset)
            self.angle_offset.set(getattr(default_prof, 'angle_offset', 0.0))
            self.selected_profile.set(profiles.default_profile)
        else:
            saved = load_saved_offset()
            if saved:
                self.x_offset.set(saved.x_offset)
                self.y_offset.set(saved.y_offset)
                self.angle_offset.set(0.0)  # Legacy profiles don't have angle offset
                self.angle_offset.set(0.0)  # Legacy profiles don't have angle offset
        
        # Profile management section
        profile_frame = ttk.LabelFrame(left_frame, text="  📋 Offset Profiles  ", padding="8", style='TLabelframe')
        profile_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=5)
        profile_frame.columnconfigure(1, weight=1)
        
        # Profile selection
        ttk.Label(profile_frame, text="Select Profile:", style='Card.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.profile_combo = ttk.Combobox(profile_frame, textvariable=self.selected_profile, 
                                         state='readonly', style='TCombobox')
        self.profile_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=5)
        self.profile_combo.bind('<<ComboboxSelected>>', self.load_selected_profile)
        self.refresh_profile_list(include_legacy=True)
        
        # Profile action buttons
        btn_frame = ttk.Frame(profile_frame, style='TFrame')
        btn_frame.grid(row=0, column=2, pady=5)
        ttk.Button(btn_frame, text="Load Default", command=self.load_default_profile, 
                  style='TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Set as Default", command=self.set_as_default_profile, 
                  style='TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Delete", command=self.delete_current_profile, 
                  style='TButton').pack(side=tk.LEFT, padx=2)
        
        # Profile info display
        self.profile_info_label = ttk.Label(profile_frame, text="No profile selected", 
                                           style='Card.TLabel', font=('Segoe UI', 9), 
                                           foreground='#808080')
        self.profile_info_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        # New profile section
        new_profile_frame = ttk.LabelFrame(left_frame, text="  ➕ Save New Profile  ", padding="8", style='TLabelframe')
        new_profile_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=5)
        new_profile_frame.columnconfigure(1, weight=1)
        
        ttk.Label(new_profile_frame, text="Profile Name:", style='Card.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Entry(new_profile_frame, textvariable=self.profile_name, style='TEntry').grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=5)
        
        ttk.Label(new_profile_frame, text="Description:", style='Card.TLabel').grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Entry(new_profile_frame, textvariable=self.profile_description, style='TEntry').grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=5)
        
        ttk.Label(new_profile_frame, text="Paper Size:", style='Card.TLabel').grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        paper_combo = ttk.Combobox(new_profile_frame, textvariable=self.profile_paper_size, 
                                   values=[p.value for p in PaperSize], state='readonly', style='TCombobox')
        paper_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(new_profile_frame, text="X Offset (pixels):", style='Card.TLabel').grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Spinbox(new_profile_frame, from_=-1000, to=1000, textvariable=self.x_offset, 
                   width=10, style='TSpinbox').grid(row=3, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(new_profile_frame, text="Y Offset (pixels):", style='Card.TLabel').grid(row=4, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Spinbox(new_profile_frame, from_=-1000, to=1000, textvariable=self.y_offset, 
                   width=10, style='TSpinbox').grid(row=4, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(new_profile_frame, text="Angle Offset (degrees):", style='Card.TLabel').grid(row=5, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Spinbox(new_profile_frame, from_=-45, to=45, textvariable=self.angle_offset, increment=0.1,
                   width=10, style='TSpinbox', format="%.1f").grid(row=5, column=1, sticky=tk.W, pady=5)
        
        ttk.Button(new_profile_frame, text="💾 Save Current Settings as Profile", 
                  command=self.save_current_as_profile, style='Accent.TButton').grid(row=6, column=0, columnspan=2, pady=(10, 0))
        
        # Offset settings
        offset_frame = ttk.LabelFrame(left_frame, text="  ⚙️ Offset Settings  ", padding="8", style='TLabelframe')
        offset_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=5)
        offset_frame.columnconfigure(1, weight=1)
        
        ttk.Label(offset_frame, text="Input PDF:", style='Card.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.input_pdf_path = tk.StringVar(value=os.path.join('game', 'output', 'game.pdf'))
        ttk.Entry(offset_frame, textvariable=self.input_pdf_path, style='TEntry').grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=5)
        ttk.Button(offset_frame, text="Browse...", command=self.browse_input_pdf, style='TButton').grid(row=0, column=2, pady=5)
        
        ttk.Label(offset_frame, text="Output PDF:", style='Card.TLabel').grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.offset_output_path = tk.StringVar(value="")
        ttk.Entry(offset_frame, textvariable=self.offset_output_path, style='TEntry').grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=5)
        ttk.Button(offset_frame, text="Save As...", command=self.browse_offset_output, style='TButton').grid(row=1, column=2, pady=5)
        ttk.Label(offset_frame, text="(Leave empty for auto-naming: *_offset.pdf)", 
                 font=('Segoe UI', 8), foreground='#808080', style='Card.TLabel').grid(row=2, column=1, sticky=tk.W)
        
        ttk.Label(offset_frame, text="X Offset (pixels):", style='Card.TLabel').grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Spinbox(offset_frame, from_=-1000, to=1000, textvariable=self.x_offset, 
                   width=10, style='TSpinbox').grid(row=3, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(offset_frame, text="Y Offset (pixels):", style='Card.TLabel').grid(row=4, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Spinbox(offset_frame, from_=-1000, to=1000, textvariable=self.y_offset, 
                   width=10, style='TSpinbox').grid(row=4, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(offset_frame, text="Angle Offset (degrees):", style='Card.TLabel').grid(row=5, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Spinbox(offset_frame, from_=-45, to=45, textvariable=self.angle_offset, increment=0.1,
                   width=10, style='TSpinbox', format="%.1f").grid(row=5, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(offset_frame, text="PPI:", style='Card.TLabel').grid(row=6, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.offset_ppi = tk.IntVar(value=300)
        ttk.Spinbox(offset_frame, from_=72, to=600, textvariable=self.offset_ppi, 
                   width=10, style='TSpinbox').grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # Info panel (collapsible, hidden by default)
        self.info_visible = tk.BooleanVar(value=False)
        info_toggle_frame = ttk.Frame(left_frame, style='TFrame')
        info_toggle_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=5)
        
        self.info_toggle_btn = ttk.Button(info_toggle_frame, text="▶ Show Information", 
                                         command=self.toggle_offset_info, style='TButton')
        self.info_toggle_btn.pack(fill=tk.X)
        
        self.info_frame = ttk.LabelFrame(left_frame, text="  ℹ️ Information  ", padding="8", style='TLabelframe')
        # Don't grid it initially - it's hidden by default
        
        info_text = ("Offset Profiles let you save multiple printer configurations for different paper sizes.\n\n"
                    "• Create profiles for each printer/paper combination\n"
                    "• Load profiles quickly to apply saved offsets\n"
                    "• Set a default profile for automatic use\n\n"
                    "Offset directions:\n"
                    "• Positive X moves cards right, Negative X moves left\n"
                    "• Positive Y moves cards down, Negative Y moves up\n"
                    "• Positive angle rotates clockwise, Negative rotates counter-clockwise")
        ttk.Label(self.info_frame, text=info_text, style='Card.TLabel', 
                 font=('Segoe UI', 9), foreground='#a0a0a0', justify=tk.LEFT).pack(anchor=tk.W)
        
        # Apply button
        button_frame = ttk.Frame(left_frame, style='TFrame')
        button_frame.grid(row=4, column=0, pady=(8, 8), padx=5)
        
        self.apply_offset_btn = ttk.Button(button_frame, text="⚙️ Apply Offset", 
                                          command=self.start_apply_offset, style='Accent.TButton')
        self.apply_offset_btn.pack(pady=5, ipadx=30, ipady=5)
        
        # Right column - Progress
        right_frame = ttk.Frame(parent, style='TFrame')
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        
        # Progress area
        progress_frame = ttk.LabelFrame(right_frame, text="  📊 Progress  ", padding="12", style='TLabelframe')
        progress_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(0, weight=1)
        
        # Create scrollbar that only shows when needed
        offset_progress_scrollbar = ttk.Scrollbar(progress_frame, orient='vertical')
        
        self.offset_progress_text = tk.Text(progress_frame, 
                                            state='disabled', wrap=tk.WORD,
                                            bg='#1e1e1e', fg='#d4d4d4',
                                            font=('Consolas', 9),
                                            relief='solid', borderwidth=1,
                                            padx=10, pady=10,
                                            yscrollcommand=offset_progress_scrollbar.set)
        offset_progress_scrollbar.config(command=self.offset_progress_text.yview)
        
        self.offset_progress_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        offset_progress_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        offset_progress_scrollbar.grid_remove()  # Hide initially
        
        # Auto-hide scrollbar when not needed
        def _offset_scrollbar_autohide(*args):
            offset_progress_scrollbar.set(*args)
            if float(args[0]) == 0.0 and float(args[1]) == 1.0:
                offset_progress_scrollbar.grid_remove()
            else:
                offset_progress_scrollbar.grid()
        self.offset_progress_text.config(yscrollcommand=_offset_scrollbar_autohide)
        
        # Configure text tags
        self.offset_progress_text.tag_config('success', foreground='#4ec9b0')
        self.offset_progress_text.tag_config('error', foreground='#f48771')
        self.offset_progress_text.tag_config('info', foreground='#9cdcfe')
    
    def browse_directory(self, var):
        """Browse for a directory"""
        directory = filedialog.askdirectory(title="Select Directory")
        if directory:
            var.set(directory)
    
    def open_created_pdf(self):
        """Open the last created PDF file"""
        if not self.last_created_pdf or not os.path.exists(self.last_created_pdf):
            messagebox.showerror("Error", "PDF file not found.")
            return
        
        try:
            if sys.platform == 'win32':
                os.startfile(self.last_created_pdf)
            elif sys.platform == 'darwin':
                import subprocess
                subprocess.run(['open', self.last_created_pdf])
            else:
                import subprocess
                subprocess.run(['xdg-open', self.last_created_pdf])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open PDF:\n{e}")
    
    def reset_directory(self, var, default_path):
        """Reset a directory to its default value"""
        var.set(default_path)
    
    def update_back_card_list(self):
        """Update the back card selection dropdown based on available files"""
        back_dir = self.back_dir.get()
        
        if not back_dir or not os.path.isdir(back_dir):
            self.back_card_combo['values'] = ["(Auto-detect)"]
            self.selected_back_card.set("(Auto-detect)")
            return
        
        try:
            # Get all non-.md files from back directory
            files = [f for f in os.listdir(back_dir) 
                    if os.path.isfile(os.path.join(back_dir, f)) and not f.endswith(".md")]
            
            if len(files) == 0:
                self.back_card_combo['values'] = ["(No backs available)"]
                self.selected_back_card.set("(No backs available)")
            elif len(files) == 1:
                # Only one back, auto-select it
                self.back_card_combo['values'] = [files[0]]
                self.selected_back_card.set(files[0])
            else:
                # Multiple backs, let user choose
                values = ["(Auto-detect)"] + files
                self.back_card_combo['values'] = values
                # Keep current selection if valid, otherwise reset to auto-detect
                if self.selected_back_card.get() not in values:
                    self.selected_back_card.set("(Auto-detect)")
        except Exception as e:
            print(f"Error updating back card list: {e}")
            self.back_card_combo['values'] = ["(Auto-detect)"]
            self.selected_back_card.set("(Auto-detect)")
    
    def open_user_data_folder(self):
        """Open the user data folder in file explorer"""
        import subprocess
        user_data_dir = self.user_data_manager.get_user_data_dir()
        
        try:
            if sys.platform == 'win32':
                os.startfile(user_data_dir)
            elif sys.platform == 'darwin':
                subprocess.run(['open', user_data_dir])
            else:
                subprocess.run(['xdg-open', user_data_dir])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{e}")
    
    def browse_pdf_output(self):
        """Browse for PDF output location"""
        filename = filedialog.asksaveasfilename(
            title="Save PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.output_pdf_path.set(filename)
    
    def browse_input_pdf(self):
        """Browse for input PDF"""
        filename = filedialog.askopenfilename(
            title="Select PDF to Offset",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.input_pdf_path.set(filename)
    
    def browse_offset_output(self):
        """Browse for offset PDF output"""
        filename = filedialog.asksaveasfilename(
            title="Save Offset PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.offset_output_path.set(filename)
    
    def browse_deck(self):
        """Open file dialog to select deck list"""
        filename = filedialog.askopenfilename(
            title="Select Deck List",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        if filename:
            # Clean up temp file if switching from pasted text to file
            self.cleanup_temp_deck_file()
            self.deck_path.set(filename)
    
    def paste_decklist_text(self):
        """Open dialog to paste decklist text"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Paste Deck List")
        dialog.geometry("700x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Apply dark theme
        dialog.configure(bg='#1e1e1e')
        
        # Main frame with padding
        main_frame = ttk.Frame(dialog, padding="15", style='TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Instructions
        instructions = ttk.Label(main_frame, 
                                text="Paste your deck list below. Each line should contain a card in your deck format.",
                                style='Card.TLabel',
                                wraplength=650)
        instructions.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Text area with scrollbar
        text_frame = ttk.Frame(main_frame, style='TFrame')
        text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        text_widget = tk.Text(text_frame, 
                             wrap=tk.WORD,
                             width=80,
                             height=25,
                             bg='#2d2d2d',
                             fg='#d4d4d4',
                             insertbackground='#d4d4d4',
                             selectbackground='#264f78',
                             selectforeground='#ffffff',
                             font=('Consolas', 10),
                             relief=tk.FLAT,
                             borderwidth=1,
                             highlightthickness=1,
                             highlightbackground='#3c3c3c',
                             highlightcolor='#007acc')
        text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Load existing content if we have a temp file
        if self.temp_deck_file and os.path.exists(self.temp_deck_file):
            try:
                with open(self.temp_deck_file, 'r', encoding='utf-8') as f:
                    text_widget.insert('1.0', f.read())
            except:
                pass
        
        text_widget.focus_set()
        
        # Button frame
        btn_frame = ttk.Frame(main_frame, style='TFrame')
        btn_frame.grid(row=2, column=0, sticky=(tk.E), pady=(10, 0))
        
        def save_text():
            content = text_widget.get('1.0', tk.END).strip()
            if not content:
                messagebox.showwarning("Empty Content", "Please paste your deck list.", parent=dialog)
                return
            
            # Clean up previous temp file
            self.cleanup_temp_deck_file()
            
            # Create temp file
            import tempfile
            fd, temp_path = tempfile.mkstemp(suffix='.txt', prefix='decklist_', text=True)
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.temp_deck_file = temp_path
                self.deck_path.set(f"[Pasted Text - {len(content.splitlines())} lines]")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save text: {str(e)}", parent=dialog)
        
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, style='TButton').grid(row=0, column=0, padx=(0, 5))
        ttk.Button(btn_frame, text="Use This Text", command=save_text, style='TButton').grid(row=0, column=1)
    
    def cleanup_temp_deck_file(self):
        """Remove temporary deck file if it exists"""
        if self.temp_deck_file and os.path.exists(self.temp_deck_file):
            try:
                os.unlink(self.temp_deck_file)
            except:
                pass
            self.temp_deck_file = None
    
    def refresh_profile_list(self, include_legacy=True):
        """Refresh the profile dropdown list"""
        profile_list = []
        
        # Check if legacy offset exists and add it if requested
        if include_legacy:
            legacy_offset = load_saved_offset()
            if legacy_offset:
                profile_list.append("(Legacy Saved Offset)")
        
        # Add all saved profiles
        profile_list.extend(list_offset_profiles())
        
        self.profile_combo['values'] = profile_list
        if self.selected_profile.get() not in profile_list:
            self.selected_profile.set("")
        # Only update profile info if the label has been created
        if hasattr(self, 'profile_info_label'):
            self.update_profile_info()
    
    def load_selected_profile(self, event=None):
        """Load the selected profile from dropdown"""
        profile_name = self.selected_profile.get()
        if not profile_name:
            return
        
        # Handle legacy offset
        if profile_name == "(Legacy Saved Offset)":
            legacy = load_saved_offset()
            if legacy:
                self.x_offset.set(legacy.x_offset)
                self.y_offset.set(legacy.y_offset)
                self.angle_offset.set(0.0)  # Legacy profiles don't have angle
                self.update_profile_info()
                self.offset_log_message(f"📋 Loaded legacy saved offset")
            return
        
        # Handle named profiles
        profile = load_offset_profile(profile_name)
        if profile:
            self.x_offset.set(profile.x_offset)
            self.y_offset.set(profile.y_offset)
            self.angle_offset.set(getattr(profile, 'angle_offset', 0.0))
            self.update_profile_info()
            self.offset_log_message(f"📋 Loaded profile: {profile_name}")
    
    def load_default_profile(self):
        """Load the default offset profile"""
        profiles = load_offset_profiles()
        if not profiles.default_profile:
            messagebox.showinfo("No Default", "No default profile is set.")
            return
        
        if profiles.default_profile in profiles.profiles:
            self.selected_profile.set(profiles.default_profile)
            self.load_selected_profile()
        else:
            messagebox.showerror("Error", "Default profile not found!")
    
    def set_as_default_profile(self):
        """Set the currently selected profile as default"""
        profile_name = self.selected_profile.get()
        if not profile_name:
            messagebox.showwarning("No Selection", "Please select a profile first.")
            return
        
        if set_default_offset_profile(profile_name):
            self.update_profile_info()
            self.refresh_pdf_profile_list()  # Update PDF tab to show new default
            messagebox.showinfo("Success", f"'{profile_name}' set as default profile!")
    
    def delete_current_profile(self):
        """Delete the currently selected profile"""
        profile_name = self.selected_profile.get()
        if not profile_name:
            messagebox.showwarning("No Selection", "Please select a profile to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Delete profile '{profile_name}'?"):
            if delete_offset_profile(profile_name):
                self.refresh_profile_list()
                self.refresh_pdf_profile_list()  # Also remove from PDF tab
                messagebox.showinfo("Deleted", f"Profile '{profile_name}' deleted.")
    
    def save_current_as_profile(self):
        """Save current offset settings as a new profile"""
        name = self.profile_name.get().strip()
        if not name:
            messagebox.showwarning("Missing Name", "Please enter a profile name.")
            return
        
        description = self.profile_description.get().strip()
        paper_size = self.profile_paper_size.get()
        
        save_offset_profile(
            name=name,
            x_offset=self.x_offset.get(),
            y_offset=self.y_offset.get(),
            paper_size=paper_size,
            description=description,
            angle_offset=self.angle_offset.get()
        )
        
        # Clear form and refresh lists in both tabs
        self.profile_name.set("")
        self.profile_description.set("")
        self.refresh_profile_list()
        self.refresh_pdf_profile_list()  # Also refresh PDF tab profile list
        self.selected_profile.set(name)
        self.update_profile_info()
        
        messagebox.showinfo("Success", f"Profile '{name}' saved!")
    
    def update_profile_info(self):
        """Update the profile information label"""
        profile_name = self.selected_profile.get()
        if not profile_name:
            self.profile_info_label.config(text="No profile selected", foreground='#808080')
            return
        
        # Handle legacy offset
        if profile_name == "(Legacy Saved Offset)":
            legacy = load_saved_offset()
            if legacy:
                info_text = f"Legacy saved offset | Offset: ({legacy.x_offset}, {legacy.y_offset})"
                self.profile_info_label.config(text=info_text, foreground='#9cdcfe')
            else:
                self.profile_info_label.config(text="Legacy offset not found", foreground='#f48771')
            return
        
        # Handle named profiles
        profile = load_offset_profile(profile_name)
        if not profile:
            self.profile_info_label.config(text="Profile not found", foreground='#f48771')
            return
        
        profiles = load_offset_profiles()
        is_default = profiles.default_profile == profile_name
        default_text = " [DEFAULT]" if is_default else ""
        
        angle_text = f", {profile.angle_offset:.1f}°" if hasattr(profile, 'angle_offset') and profile.angle_offset != 0.0 else ""
        
        info_text = (f"{profile.description} | "
                    f"Paper: {profile.paper_size} | "
                    f"Offset: ({profile.x_offset}, {profile.y_offset}{angle_text})"
                    f"{default_text}")
        
        self.profile_info_label.config(text=info_text, foreground='#4ec9b0')
    
    def refresh_pdf_profile_list(self, include_legacy=True):
        """Refresh the PDF tab's profile dropdown list"""
        profile_list = ["(None - No Offset)"]
        
        # Check if legacy offset exists and add it if requested
        if include_legacy:
            legacy_offset = load_saved_offset()
            if legacy_offset:
                profile_list.append("(Legacy Saved Offset)")
        
        # Add all saved profiles
        profile_list.extend(list_offset_profiles())
        
        self.pdf_profile_combo['values'] = profile_list
        
        # If current selection is not in the list, try to set default or fallback to no offset
        if self.pdf_selected_profile.get() not in profile_list:
            profiles = load_offset_profiles()
            if profiles.default_profile and profiles.default_profile in profiles.profiles:
                self.pdf_selected_profile.set(profiles.default_profile)
            else:
                self.pdf_selected_profile.set("(None - No Offset)")
        
        # Update the profile info display
        if hasattr(self, 'pdf_profile_info_label'):
            self.update_pdf_profile_info()
    
    def update_pdf_profile_info(self, event=None):
        """Update the PDF profile information label"""
        profile_name = self.pdf_selected_profile.get()
        
        if not profile_name or profile_name == "(None - No Offset)":
            self.pdf_profile_info_label.config(text="No offset will be applied", foreground='#808080')
            return
        
        # Handle legacy offset
        if profile_name == "(Legacy Saved Offset)":
            legacy = load_saved_offset()
            if legacy:
                info_text = f"Legacy saved offset | Offset: ({legacy.x_offset}, {legacy.y_offset})"
                self.pdf_profile_info_label.config(text=info_text, foreground='#9cdcfe')
            else:
                self.pdf_profile_info_label.config(text="Legacy offset not found", foreground='#f48771')
            return
        
        # Handle named profiles
        profile = load_offset_profile(profile_name)
        if not profile:
            self.pdf_profile_info_label.config(text="Profile not found", foreground='#f48771')
            return
        
        profiles = load_offset_profiles()
        is_default = profiles.default_profile == profile_name
        default_text = " [DEFAULT]" if is_default else ""
        
        angle_text = f", {profile.angle_offset:.1f}°" if hasattr(profile, 'angle_offset') and profile.angle_offset != 0.0 else ""
        
        info_text = (f"{profile.description} | "
                    f"Paper: {profile.paper_size} | "
                    f"Offset: ({profile.x_offset}, {profile.y_offset}{angle_text})"
                    f"{default_text}")
        
        self.pdf_profile_info_label.config(text=info_text, foreground='#4ec9b0')
    
    def check_message_queue(self):
        """Check for messages from worker thread and update GUI"""
        try:
            while True:
                msg = self.message_queue.get_nowait()
                msg_type = msg.get('type')
                
                if msg_type == 'log':
                    self._log_message_internal(msg['text'], msg.get('tag'))
                elif msg_type == 'progress':
                    self._update_progress_internal(msg['current'], msg['total'], msg.get('text'))
                elif msg_type == 'card':
                    self._update_current_card_internal(msg['card_name'], msg.get('details'))
                elif msg_type == 'complete':
                    self._fetch_complete_internal(msg['success'], msg.get('message'))
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_message_queue)
    
    def log_message(self, message, tag=None):
        """Add a message to the progress text area (thread-safe)"""
        self.message_queue.put({'type': 'log', 'text': message, 'tag': tag})
    
    def _log_message_internal(self, message, tag=None):
        """Internal method to update log (must be called from main thread)"""
        self.progress_text.configure(state='normal')
        if tag:
            self.progress_text.insert(tk.END, message + "\n", tag)
        else:
            self.progress_text.insert(tk.END, message + "\n")
        self.progress_text.see(tk.END)
        self.progress_text.configure(state='disabled')
    
    def update_progress(self, current, total, text=None):
        """Update progress (no-op since we removed the progress bar)"""
        pass
    
    def update_current_card(self, card_name, details=None):
        """Update currently processing card (no-op since we removed card preview)"""
        pass
    
    def validate_inputs(self):
        """Validate user inputs before starting fetch"""
        if not self.deck_path.get():
            messagebox.showerror("Error", "Please select a deck list file or paste deck text.")
            return False
        
        # Check if using temp file (pasted text) or regular file
        deck_file = self.temp_deck_file if self.temp_deck_file else self.deck_path.get()
        if not os.path.isfile(deck_file):
            messagebox.showerror("Error", f"File not found: {deck_file}")
            return False
        
        return True
    
    def toggle_fetch(self):
        """Toggle between starting and canceling fetch"""
        if self.is_fetching:
            # Cancel fetch
            if messagebox.askyesno("Cancel Fetch", "Are you sure you want to cancel the current fetch operation?"):
                self.cancel_fetch = True
                self.log_message("", 'warning')
                self.log_message("⚠️ Canceling fetch operation...", 'warning')
                self.fetch_btn.configure(state='disabled', text="⏳ Canceling...")
        else:
            # Start fetch
            self.start_fetch()
    
    def cleanup_images(self):
        """Clean up downloaded images from game directories"""
        if self.is_fetching:
            messagebox.showwarning("Warning", "Cannot cleanup while fetching is in progress.")
            return
        
        # Ask for confirmation
        if not messagebox.askyesno("Confirm Cleanup", 
                                   "This will delete all downloaded card images from:\\n\\n" +
                                   "• game/front/\\n" +
                                   "• game/double_sided/\\n\\n" +
                                   "Are you sure?"):
            return
        
        try:
            root_path = 'game'
            image_folders = ['front', 'double_sided']
            deleted_count = 0
            
            self.log_message("", 'info')
            self.log_message("═" * 70, 'info')
            self.log_message("🧹 Starting cleanup...", 'info')
            
            for folder_name in image_folders:
                working_path = os.path.join(root_path, folder_name)
                
                if not os.path.exists(working_path):
                    continue
                
                for item in os.listdir(working_path):
                    full_path = os.path.join(working_path, item)
                    
                    # Skip EMPTY.md files
                    if os.path.basename(full_path) == 'EMPTY.md':
                        continue
                    
                    try:
                        if os.path.isfile(full_path):
                            os.remove(full_path)
                            self.log_message(f"🗑️  Deleted file: {full_path}", 'info')
                            deleted_count += 1
                        elif os.path.isdir(full_path):
                            import shutil
                            shutil.rmtree(full_path)
                            self.log_message(f"🗑️  Deleted directory: {full_path}", 'info')
                            deleted_count += 1
                    except Exception as e:
                        self.log_message(f"❌ Error deleting {full_path}: {e}", 'error')
            
            self.log_message("", 'success')
            self.log_message(f"✅ Cleanup complete! Deleted {deleted_count} item{'s' if deleted_count != 1 else ''}", 'success')
            self.log_message("═" * 70, 'success')
            
            messagebox.showinfo("Cleanup Complete", f"Deleted {deleted_count} item{'s' if deleted_count != 1 else ''}")
            
        except Exception as e:
            error_msg = f"Error during cleanup: {str(e)}"
            self.log_message(f"❌ {error_msg}", 'error')
            messagebox.showerror("Cleanup Error", error_msg)
    
    def start_fetch(self):
        """Start the fetch process in a background thread"""
        if not self.validate_inputs():
            return
        
        if self.is_fetching:
            messagebox.showwarning("Warning", "A fetch operation is already in progress.")
            return
        
        # Clear previous progress
        self.progress_text.configure(state='normal')
        self.progress_text.delete(1.0, tk.END)
        self.progress_text.configure(state='disabled')
        
        # Reset cancel flag and update button
        self.cancel_fetch = False
        self.fetch_btn.configure(text="⏹️ Cancel Fetch", style='Cancel.TButton')
        self.cleanup_btn.configure(state='disabled')
        self.is_fetching = True
        self.total_cards = 0
        self.completed_cards = 0
        
        # Run fetch in background thread
        thread = threading.Thread(target=self.fetch_cards, daemon=True)
        thread.start()
    
    def fetch_cards(self):
        """Fetch cards (runs in background thread)"""
        success = False
        error_message = None
        
        try:
            game_id = self.selected_game.get()
            plugin = self.plugin_manager.get_plugin(game_id)
            game_name = plugin.name if plugin else "Unknown Game"
            
            self.log_message("═" * 70, 'info')
            self.log_message(f"🎮 Game: {game_name}", 'info')
            
            # Display deck source (file or pasted text)
            if self.temp_deck_file:
                self.log_message(f"📄 Deck: [Pasted Text]", 'info')
            else:
                self.log_message(f"📄 Deck: {os.path.basename(self.deck_path.get())}", 'info')
            
            self.log_message(f"📋 Format: {self.deck_format.get()}", 'info')
            
            # Only show supported options for this game
            if plugin:
                if plugin.supports_art_crop:
                    self.log_message(f"🎨 Art Crop: {'Yes' if self.art_crop.get() else 'No'}", 'info')
                if plugin.supports_tokens:
                    self.log_message(f"🪙 Tokens: {'Yes' if self.tokens.get() else 'No'}", 'info')
                if plugin.supports_parallel:
                    self.log_message(f"⚡ Parallel: {'Yes' if self.parallel.get() else 'No'}", 'info')
                    if self.parallel.get():
                        self.log_message(f"👥 Workers: {self.max_workers.get()}", 'info')
                    self.log_message(f"⏱️  API Delay: {self.api_delay.get()}s", 'info')
            
            self.log_message("═" * 70, 'info')
            self.log_message("")
            
            # Custom print wrapper to capture and categorize output
            original_print = print
            def custom_print(*args, **kwargs):
                message = ' '.join(str(arg) for arg in args)
                
                # Extract card name and details for preview
                if '🎯' in message:
                    # Frame detection messages: "🎯 Card Name → frame_type (folder)"
                    try:
                        parts = message.split('🎯')[1].strip()
                        if '→' in parts:
                            card_name = parts.split('→')[0].strip()
                            frame_info = parts.split('→')[1].strip()
                            self.update_current_card(card_name, f"Type: {frame_info}")
                    except:
                        pass
                elif '💾 Saving to:' in message or '💾 Saving' in message:
                    # Save messages
                    try:
                        if 'Saving to:' in message:
                            path_part = message.split('Saving to:')[1].strip()
                            parts = path_part.split('/')
                            if len(parts) >= 2:
                                folder = parts[0]
                                filename = parts[-1]
                                card_name = filename.split('[')[0].strip()
                                set_info = ''
                                if '[' in filename and ']' in filename:
                                    set_info = filename.split('[')[1].split(']')[0]
                                if card_name:
                                    detail = f"Folder: {folder}"
                                    if set_info:
                                        detail += f" | Set: {set_info}"
                                    self.update_current_card(card_name, detail)
                    except:
                        pass
                elif '📦 Progress:' in message:
                    # Progress messages - extract card count
                    try:
                        parts = message.split('Progress:')[1].strip()
                        counts = parts.split('/')[0].strip()
                        # Don't update card name for progress messages
                    except:
                        pass
                
                # Categorize messages by content
                if '✅' in message or 'complete' in message.lower() or 'success' in message.lower():
                    tag = 'success'
                elif '❌' in message or 'error' in message.lower() or 'failed' in message.lower():
                    tag = 'error'
                elif '⚠️' in message or 'warning' in message.lower():
                    tag = 'warning'
                elif '🎯' in message or '💾' in message:
                    tag = 'card'
                elif '🚀' in message or '📦' in message or '📖' in message:
                    tag = 'info'
                else:
                    tag = None
                
                self.log_message(message, tag)
                
                # Track progress from download messages
                if 'Progress:' in message and '/' in message:
                    try:
                        parts = message.split('Progress:')[1].strip().split('/')
                        current = int(parts[0].strip())
                        total = int(parts[1].split()[0].strip())
                        self.update_progress(current, total)
                    except:
                        pass
            
            # Replace print temporarily
            import builtins
            builtins.print = custom_print
            
            try:
                # Get selected plugin
                game_id = self.selected_game.get()
                plugin = self.plugin_manager.get_plugin(game_id)
                
                if not plugin:
                    self.log_message(f"❌ Plugin not found for game: {game_id}", 'error')
                    return
                
                self.log_message(f"🎮 Game: {plugin.name}", 'info')
                
                # Set up directories - use paths from settings
                front_directory = self.front_dir.get()
                double_sided_directory = self.double_sided_dir.get()
                os.makedirs(front_directory, exist_ok=True)
                os.makedirs(double_sided_directory, exist_ok=True)
                
                # Handle different plugins
                if game_id == "mtg":
                    # MTG-specific handling (original code)
                    from plugins.mtg.deck_formats import DeckFormat
                    from plugins.mtg.scryfall import get_handle_card as scryfall_get_handle_card
                    from plugins.mtg.deck_formats import parse_deck
                    
                    format_enum = DeckFormat(self.deck_format.get())
                    
                    get_handle_card = scryfall_get_handle_card(
                        self.ignore_set_collector.get(),
                        self.prefer_older_sets.get(),
                        set(),  # prefer_set (not implemented in GUI yet)
                        self.prefer_showcase.get(),
                        self.prefer_extra_art.get(),
                        self.tokens.get(),
                        self.art_crop.get(),
                        self.parallel.get(),
                        self.max_workers.get(),
                        self.api_delay.get(),
                        front_directory,
                        double_sided_directory,
                        cancel_check=lambda: self.cancel_fetch  # Pass cancel check
                    )
                    
                    # Read and parse deck
                    self.log_message("📖 Reading deck list...", 'info')
                    if self.parallel.get():
                        self.log_message("📊 Building download queue (fetching card metadata)...", 'info')
                    
                    import time
                    fetch_start_time = time.time()
                    
                    # Use temp file if available (pasted text), otherwise use selected file
                    deck_file_path = self.temp_deck_file if self.temp_deck_file else self.deck_path.get()
                    
                    with open(deck_file_path, 'r', encoding='utf-8') as deck_file:
                        deck_text = deck_file.read()
                        parse_deck(deck_text, format_enum, get_handle_card)
                    
                    # Check if user canceled
                    if self.cancel_fetch:
                        self.log_message("", 'warning')
                        self.log_message("⚠️ Fetch canceled by user", 'warning')
                        error_message = 'Fetch canceled by user'
                        return
                    
                    fetch_elapsed_time = time.time() - fetch_start_time
                    
                    # Process parallel downloads if enabled
                    if self.parallel.get() and hasattr(get_handle_card, 'download_queue'):
                        from plugins.mtg.download_manager import DownloadQueue
                        dl_queue = get_handle_card.download_queue
                        if dl_queue.size() > 0:
                            self.log_message(f"✅ Queued {dl_queue.size()} cards for download")
                            self.log_message("")
                            downloader = get_handle_card.downloader
                            result = downloader.download_cards_parallel(
                                tasks=dl_queue.get_all_tasks(),
                                fetch_function=get_handle_card.fetch_card_art,
                                front_dir=get_handle_card.front_img_dir,
                                double_sided_dir=get_handle_card.double_sided_dir,
                                art_crop=get_handle_card.art_crop,
                                fetch_time=fetch_elapsed_time,  # Pass fetch time to include in summary
                                cancel_check=lambda: self.cancel_fetch  # Pass cancel check function
                            )
                
                elif game_id == "lorcana":
                    # Lorcana-specific handling
                    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'plugins', 'lorcana'))
                    from plugins.lorcana.deck_formats import DeckFormat as LorcanaDeckFormat
                    from plugins.lorcana.deck_formats import parse_dreamborn_list
                    from plugins.lorcana.lorcast import get_handle_card as lorcast_get_handle_card
                    
                    self.log_message("📖 Reading Lorcana deck list...", 'info')
                    
                    # Use temp file if available (pasted text), otherwise use selected file
                    deck_file_path = self.temp_deck_file if self.temp_deck_file else self.deck_path.get()
                    
                    with open(deck_file_path, 'r', encoding='utf-8') as deck_file:
                        deck_text = deck_file.read()
                        parse_dreamborn_list(deck_text, lorcast_get_handle_card(front_directory))
                
                elif game_id == "yugioh":
                    # Yu-Gi-Oh! specific handling
                    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'plugins', 'yugioh'))
                    from plugins.yugioh.deck_formats import DeckFormat as YugiohDeckFormat, parse_deck as yugioh_parse
                    from plugins.yugioh.ygoprodeck import get_handle_card as yugioh_get_handle_card
                    
                    format_enum = YugiohDeckFormat(self.deck_format.get())
                    
                    self.log_message("📖 Reading Yu-Gi-Oh! deck list...", 'info')
                    
                    # Use temp file if available (pasted text), otherwise use selected file
                    deck_file_path = self.temp_deck_file if self.temp_deck_file else self.deck_path.get()
                    
                    with open(deck_file_path, 'r', encoding='utf-8') as deck_file:
                        deck_text = deck_file.read()
                        yugioh_parse(deck_text, format_enum, yugioh_get_handle_card(front_directory))
                
                else:
                    # Generic handler for other plugins
                    self.log_message(f"⚠️ Plugin '{plugin.name}' is registered but fetch implementation is pending", 'warning')
                    self.log_message("📧 Please check the plugin documentation or implement the fetch function", 'info')
            finally:
                # Restore original print
                builtins.print = original_print
            
            # Check if user canceled after downloads
            if self.cancel_fetch:
                self.log_message("", 'warning')
                self.log_message("═" * 70, 'warning')
                self.log_message("⚠️ Fetch canceled by user", 'warning')
                self.log_message("═" * 70, 'warning')
                error_message = 'Fetch canceled by user'
                return
            
            self.log_message("")
            self.log_message("═" * 70, 'success')
            self.log_message("✅ All cards fetched successfully!", 'success')
            self.log_message("═" * 70, 'success')
            
            success = True
            
        except Exception as e:
            import traceback
            self.log_message("")
            self.log_message("═" * 70, 'error')
            self.log_message(f"❌ ERROR: {str(e)}", 'error')
            self.log_message("═" * 70, 'error')
            
            # Log full traceback to console for debugging
            traceback.print_exc()
            
            error_message = str(e)
        finally:
            # Always send exactly one completion message to reset UI state
            print(f"DEBUG: Finally block - success={success}, error_message={error_message}")
            self.message_queue.put({
                'type': 'complete', 
                'success': success, 
                'message': error_message if error_message else 'Cards fetched successfully!'
            })
            print(f"DEBUG: Completion message sent to queue")
    
    def _fetch_complete_internal(self, success, message=None):
        """Called when fetch completes (must be called from main thread)"""
        # Re-enable buttons and reset state
        self.fetch_btn.configure(text='🚀 Start Fetching Cards', style='Accent.TButton', state='normal')
        self.cleanup_btn.configure(state='normal')
        self.is_fetching = False
        self.cancel_fetch = False
        
        if success:
            if not message or "cancel" not in message.lower():
                messagebox.showinfo("Success", message or "Cards fetched successfully!")
        else:
            if message and "cancel" in message.lower():
                # Fetch was canceled by user
                pass  # Don't show error dialog for user cancellation
            else:
                messagebox.showerror("Error", message or "An error occurred during fetch")
    
    def start_create_pdf(self):
        """Start PDF creation in background thread"""
        if self.is_creating_pdf:
            messagebox.showwarning("Warning", "PDF creation already in progress.")
            return
        
        # Refresh back card list to ensure it's up to date
        self.update_back_card_list()
        
        # Validate inputs
        if not os.path.exists(self.front_dir.get()):
            messagebox.showerror("Error", f"Front directory does not exist: {self.front_dir.get()}")
            return
        
        # Clear previous output
        self.pdf_progress_text.configure(state='normal')
        self.pdf_progress_text.delete(1.0, tk.END)
        self.pdf_progress_text.configure(state='disabled')
        
        self.create_pdf_btn.configure(state='disabled', text="⏳ Creating PDF...")
        self.is_creating_pdf = True
        
        # Run in background thread
        thread = threading.Thread(target=self.create_pdf_worker, daemon=True)
        thread.start()
    
    def create_pdf_worker(self):
        """Worker thread for PDF creation"""
        success = False
        error_message = None
        
        try:
            # Redirect print to GUI
            original_print = print
            def custom_print(*args, **kwargs):
                message = ' '.join(str(arg) for arg in args)
                self.pdf_log_message(message)
            
            import builtins
            builtins.print = custom_print
            
            try:
                self.pdf_log_message("═" * 70)
                self.pdf_log_message("📄 Creating PDF...")
                self.pdf_log_message(f"Card Size: {self.card_size.get()}")
                self.pdf_log_message(f"Paper Size: {self.paper_size.get()}")
                self.pdf_log_message(f"Output: {self.output_pdf_path.get()}")
                
                # Determine offset profile to use
                selected_profile = self.pdf_selected_profile.get()
                offset_profile_name = None
                use_legacy = False
                
                if selected_profile == "(Legacy Saved Offset)":
                    use_legacy = True
                    self.pdf_log_message("📋 Using legacy saved offset")
                elif selected_profile and selected_profile != "(None - No Offset)":
                    offset_profile_name = selected_profile
                    self.pdf_log_message(f"📋 Offset Profile: {offset_profile_name}")
                else:
                    self.pdf_log_message("📋 Offset Profile: None")
                
                self.pdf_log_message("═" * 70)
                self.pdf_log_message("")
                
                # Prepare skip parameter
                skip_list = tuple()  # Could add GUI input for this later
                
                # Create PDF
                generate_pdf(
                    self.front_dir.get(),
                    self.back_dir.get(),
                    self.double_sided_dir.get(),
                    self.output_pdf_path.get(),
                    self.output_images.get(),
                    self.card_size.get(),
                    self.paper_size.get(),
                    self.registration.get(),
                    self.only_fronts.get(),
                    self.crop_amount.get() if self.crop_amount.get() else None,
                    self.extend_corners.get(),
                    self.ppi.get(),
                    self.pdf_quality.get(),
                    skip_list,
                    use_legacy,  # load_offset (use legacy if selected)
                    offset_profile_name,  # offset_profile parameter
                    self.pdf_name.get() if self.pdf_name.get() else None,
                    self.selected_back_card.get() if self.selected_back_card.get() else None  # selected back card
                )
                
                self.pdf_log_message("")
                self.pdf_log_message("═" * 70)
                self.pdf_log_message("✅ PDF created successfully!")
                self.pdf_log_message("═" * 70)
                
                # Store the created PDF path
                self.last_created_pdf = self.output_pdf_path.get()
                
                success = True
                
            finally:
                builtins.print = original_print
                
        except Exception as e:
            import traceback
            try:
                traceback.print_exc()
            except:
                pass  # Ignore errors in error reporting
            
            error_message = str(e)
            try:
                self.pdf_log_message("")
                self.pdf_log_message("═" * 70)
                self.pdf_log_message(f"❌ ERROR: {error_message}")
                self.pdf_log_message("═" * 70)
            except:
                pass  # Ignore errors in logging
        
        finally:
            # Always reset the button state, no matter what happens
            self.root.after(0, lambda: self.pdf_creation_complete(success, error_message))
    
    def pdf_log_message(self, message):
        """Thread-safe log message for PDF tab"""
        def log():
            self.pdf_progress_text.configure(state='normal')
            self.pdf_progress_text.insert(tk.END, message + '\n')
            self.pdf_progress_text.see(tk.END)
            self.pdf_progress_text.configure(state='disabled')
        
        self.root.after(0, log)
    
    def pdf_creation_complete(self, success, message=None):
        """Called when PDF creation completes"""
        self.create_pdf_btn.configure(state='normal', text="📄 Create PDF")
        self.is_creating_pdf = False
        
        if success:
            # Ask if user wants to open the PDF
            if messagebox.askyesno("Success", "PDF created successfully!\n\nWould you like to open it now?"):
                self.open_created_pdf()
        else:
            messagebox.showerror("Error", message or "Failed to create PDF")
    
    def start_apply_offset(self):
        """Apply offset to PDF"""
        if not os.path.exists(self.input_pdf_path.get()):
            messagebox.showerror("Error", f"Input PDF not found: {self.input_pdf_path.get()}")
            return
        
        # Clear output
        self.offset_progress_text.configure(state='normal')
        self.offset_progress_text.delete(1.0, tk.END)
        self.offset_progress_text.configure(state='disabled')
        
        self.apply_offset_btn.configure(state='disabled', text="⏳ Applying...")
        
        # Run in background thread
        thread = threading.Thread(target=self.apply_offset_worker, daemon=True)
        thread.start()
    
    def apply_offset_worker(self):
        """Worker thread for offset application"""
        try:
            # Redirect output
            original_print = print
            def custom_print(*args, **kwargs):
                message = ' '.join(str(arg) for arg in args)
                self.offset_log_message(message)
            
            import builtins
            builtins.print = custom_print
            
            try:
                import pypdfium2 as pdfium
                from utilities import offset_images
                
                self.offset_log_message("═" * 70)
                self.offset_log_message(f"📄 Input PDF: {self.input_pdf_path.get()}")
                self.offset_log_message(f"⚙️ X Offset: {self.x_offset.get()}")
                self.offset_log_message(f"⚙️ Y Offset: {self.y_offset.get()}")
                self.offset_log_message(f"⚙️ Angle Offset: {self.angle_offset.get():.1f}°")
                
                # Show profile info if one is selected
                if self.selected_profile.get():
                    self.offset_log_message(f"📋 Using profile: {self.selected_profile.get()}")
                
                self.offset_log_message("═" * 70)
                self.offset_log_message("")
                
                # Load PDF
                pdf = pdfium.PdfDocument(self.input_pdf_path.get())
                
                # Get all page images
                raw_images = []
                page_count = len(pdf)
                for page_number in range(page_count):
                    self.offset_log_message(f"📖 Loading page {page_number + 1}/{page_count}")
                    page = pdf.get_page(page_number)
                    raw_images.append(page.render(self.offset_ppi.get()/72).to_pil())
                
                # Apply offset
                self.offset_log_message("")
                self.offset_log_message("⚙️ Applying offset...")
                final_images = offset_images(raw_images, self.x_offset.get(), 
                                            self.y_offset.get(), self.offset_ppi.get(),
                                            self.angle_offset.get())
                
                # Determine output path
                output_path = self.offset_output_path.get()
                if not output_path:
                    output_path = f'{self.input_pdf_path.get().removesuffix(".pdf")}_offset.pdf'
                
                # Save PDF
                self.offset_log_message(f"💾 Saving to: {output_path}")
                final_images[0].save(output_path, save_all=True, append_images=final_images[1:], 
                                    resolution=self.offset_ppi.get(), speed=0, subsampling=0, quality=100)
                
                self.offset_log_message("")
                self.offset_log_message("═" * 70)
                self.offset_log_message("✅ Offset applied successfully!")
                self.offset_log_message("═" * 70)
                
                self.root.after(0, lambda: self.offset_complete(True, output_path))
                
            finally:
                builtins.print = original_print
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.offset_log_message("")
            self.offset_log_message("═" * 70)
            self.offset_log_message(f"❌ ERROR: {str(e)}")
            self.offset_log_message("═" * 70)
            self.root.after(0, lambda: self.offset_complete(False, str(e)))
    
    def offset_log_message(self, message):
        """Thread-safe log message for offset tab"""
        def log():
            self.offset_progress_text.configure(state='normal')
            self.offset_progress_text.insert(tk.END, message + '\n')
            self.offset_progress_text.see(tk.END)
            self.offset_progress_text.configure(state='disabled')
        
        self.root.after(0, log)
    
    def offset_complete(self, success, info):
        """Called when offset completes"""
        self.apply_offset_btn.configure(state='normal', text="⚙️ Apply Offset")
        
        if success:
            messagebox.showinfo("Success", f"Offset applied successfully!\n\nSaved to:\n{info}")
        else:
            messagebox.showerror("Error", f"Failed to apply offset:\n{info}")


def main():
    root = tk.Tk()
    app = MTGCardFetcherGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
