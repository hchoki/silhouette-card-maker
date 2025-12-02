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
        self.root.geometry("1600x900")
        self.root.minsize(1400, 800)
        
        # Message queue for thread-safe GUI updates
        self.message_queue = queue.Queue()
        
        # Configure modern style
        self.setup_styles()
        
        # Initialize plugin manager
        self.plugin_manager = get_plugin_manager()
        
        # Fetch card variables
        self.selected_game = tk.StringVar(value="mtg")  # Default to MTG
        self.deck_path = tk.StringVar()
        self.deck_format = tk.StringVar(value="archidekt")
        self.art_crop = tk.BooleanVar(value=True)
        self.tokens = tk.BooleanVar(value=False)
        self.parallel = tk.BooleanVar(value=True)
        self.max_workers = tk.IntVar(value=6)
        self.api_delay = tk.DoubleVar(value=0.05)
        self.prefer_showcase = tk.BooleanVar(value=False)
        self.prefer_extra_art = tk.BooleanVar(value=False)
        self.prefer_older_sets = tk.BooleanVar(value=False)
        self.ignore_set_collector = tk.BooleanVar(value=False)
        
        # PDF creation variables
        self.front_dir = tk.StringVar(value=os.path.join('game', 'front'))
        self.back_dir = tk.StringVar(value=os.path.join('game', 'back'))
        self.double_sided_dir = tk.StringVar(value=os.path.join('game', 'double_sided'))
        self.output_pdf_path = tk.StringVar(value=os.path.join('game', 'output', 'game.pdf'))
        self.card_size = tk.StringVar(value=CardSize.STANDARD.value)
        self.paper_size = tk.StringVar(value=PaperSize.LETTER.value)
        self.registration = tk.StringVar(value=Registration.THREE.value)
        self.only_fronts = tk.BooleanVar(value=False)
        self.crop_amount = tk.StringVar(value="")
        self.extend_corners = tk.IntVar(value=0)
        self.ppi = tk.IntVar(value=300)
        self.pdf_quality = tk.IntVar(value=75)
        self.pdf_name = tk.StringVar(value="")
        
        # Offset variables
        self.x_offset = tk.IntVar(value=0)
        self.y_offset = tk.IntVar(value=0)
        self.selected_profile = tk.StringVar(value="")
        self.pdf_selected_profile = tk.StringVar(value="")  # For Create PDF tab
        self.profile_name = tk.StringVar(value="")
        self.profile_description = tk.StringVar(value="")
        self.profile_paper_size = tk.StringVar(value=PaperSize.LETTER.value)
        
        self.is_fetching = False
        self.is_creating_pdf = False
        self.total_cards = 0
        self.completed_cards = 0
        
        self.setup_ui()
        self.check_message_queue()
    
    def setup_styles(self):
        """Configure modern, attractive styles"""
        # Dark mode color scheme
        bg_color = '#1e1e1e'  # VS Code dark background
        card_bg = '#252526'  # Slightly lighter for cards
        text_color = '#d4d4d4'  # Light gray text
        entry_bg = '#3c3c3c'  # Entry field background
        entry_fg = '#ffffff'  # Entry field text - WHITE
        accent_color = '#0e639c'  # Blue accent
        accent_hover = '#1177bb'  # Lighter blue on hover
        success_color = '#4ec9b0'  # Teal
        border_color = '#3e3e42'  # Subtle borders
        
        # Configure root background
        self.root.configure(bg=bg_color)
        
        # Use option_add for more reliable styling
        self.root.option_add('*TCombobox*Listbox.background', entry_bg)
        self.root.option_add('*TCombobox*Listbox.foreground', entry_fg)
        self.root.option_add('*TCombobox*Listbox.selectBackground', accent_color)
        self.root.option_add('*TCombobox*Listbox.selectForeground', entry_fg)
        
        style = ttk.Style()
        
        # Use a modern theme as base
        try:
            style.theme_use('clam')  # Clam works better for customization
        except:
            pass
        
        # Frame styles
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, font=('Segoe UI', 10), foreground=text_color)
        style.configure('Title.TLabel', font=('Segoe UI', 20, 'bold'), foreground='#ffffff', background=bg_color)
        style.configure('Subtitle.TLabel', font=('Segoe UI', 9), foreground='#808080', background=bg_color)
        style.configure('Card.TLabel', background=card_bg, font=('Segoe UI', 10), foreground=text_color)
        
        # LabelFrame styles
        style.configure('TLabelframe', background=card_bg, borderwidth=1, relief='solid')
        style.configure('TLabelframe.Label', background=card_bg, font=('Segoe UI', 10, 'bold'), 
                       foreground='#ffffff')
        
        # Button styles - Accent button
        style.configure('Accent.TButton', 
                       font=('Segoe UI', 12, 'bold'), 
                       padding=10,
                       background=accent_color,
                       foreground='#ffffff',
                       borderwidth=0)
        style.map('Accent.TButton', 
                 background=[('active', accent_hover), ('pressed', accent_color), ('!active', accent_color)],
                 foreground=[('active', '#ffffff'), ('!active', '#ffffff'), ('disabled', '#808080')])
        
        # Regular buttons
        style.configure('TButton', 
                       background='#3c3c3c', 
                       foreground='#ffffff',
                       borderwidth=1,
                       focuscolor='none',
                       font=('Segoe UI', 9))
        style.map('TButton',
                 background=[('active', '#4c4c4c'), ('pressed', '#2c2c2c'), ('!active', '#3c3c3c')],
                 foreground=[('!active', '#ffffff')])
        
        # Checkbutton styles
        style.configure('TCheckbutton', 
                       background=card_bg, 
                       font=('Segoe UI', 10), 
                       foreground=text_color,
                       focuscolor=card_bg)
        style.map('TCheckbutton',
                 background=[('active', card_bg)],
                 foreground=[('active', text_color)])
        
        # Entry - critical for visibility
        style.configure('TEntry', 
                       fieldbackground=entry_bg,
                       background=entry_bg,
                       foreground=entry_fg,
                       insertcolor=entry_fg,
                       bordercolor=border_color,
                       lightcolor=border_color,
                       darkcolor=border_color)
        style.map('TEntry',
                 fieldbackground=[('readonly', entry_bg), ('disabled', '#2c2c2c')],
                 foreground=[('readonly', entry_fg), ('disabled', '#808080')])
        
        # Combobox - critical for visibility  
        style.configure('TCombobox',
                       fieldbackground=entry_bg,
                       background=entry_bg,
                       foreground=entry_fg,
                       arrowcolor=entry_fg,
                       bordercolor=border_color,
                       lightcolor=border_color,
                       darkcolor=border_color,
                       insertcolor=entry_fg,
                       selectbackground=accent_color,
                       selectforeground=entry_fg)
        style.map('TCombobox',
                 fieldbackground=[('readonly', entry_bg), ('disabled', '#2c2c2c')],
                 foreground=[('readonly', entry_fg), ('disabled', '#808080')],
                 selectbackground=[('readonly', accent_color)])
        
        # Spinbox - critical for visibility
        style.configure('TSpinbox',
                       fieldbackground=entry_bg,
                       background=entry_bg,
                       foreground=entry_fg,
                       arrowcolor=entry_fg,
                       bordercolor=border_color,
                       insertcolor=entry_fg)
        style.map('TSpinbox',
                 fieldbackground=[('readonly', entry_bg), ('disabled', '#2c2c2c')],
                 foreground=[('readonly', entry_fg), ('disabled', '#808080')])
        
        # Progressbar
        style.configure('TProgressbar', 
                       thickness=25, 
                       troughcolor='#3c3c3c', 
                       background=success_color,
                       bordercolor=border_color,
                       lightcolor=success_color,
                       darkcolor=success_color)
        
        # Notebook (tabs)
        style.configure('TNotebook', 
                       background=bg_color,
                       borderwidth=0,
                       tabmargins=0)
        style.configure('TNotebook.Tab',
                       background='#2d2d2d',
                       foreground=text_color,
                       padding=[20, 12],
                       font=('Segoe UI', 10),
                       borderwidth=0,
                       focuscolor='none')
        style.map('TNotebook.Tab',
                 background=[('selected', card_bg), ('active', '#3c3c3c'), ('!selected', '#2d2d2d')],
                 foreground=[('selected', accent_color), ('active', text_color), ('!selected', text_color)],
                 padding=[('selected', [20, 12]), ('!selected', [20, 12])])
    
    def setup_ui(self):
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20", style='TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Header
        header_frame = ttk.Frame(main_frame, style='TFrame')
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="🃏 Card Fetcher & PDF Creator", 
                               font=('Segoe UI', 20, 'bold'), 
                               foreground='#ffffff',
                               style='Card.TLabel')
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        subtitle_label = ttk.Label(header_frame, text="Download card game cards for proxy printing", 
                                  font=('Segoe UI', 10), 
                                  foreground='#a0a0a0',
                                  style='Card.TLabel')
        subtitle_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
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
            if canvas.bbox('all') and canvas.bbox('all')[3] <= canvas.winfo_height():
                scrollbar.grid_remove()
            else:
                scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        left_frame.bind('<Configure>', on_fetch_frame_configure)
        
        canvas.create_window((0, 0), window=left_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
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
        
        # Set initial value to MTG's display name
        initial_game_id = self.selected_game.get()
        if initial_game_id in self.game_id_to_name:
            self.game_combo.set(self.game_id_to_name[initial_game_id])
        
        # Update formats when game changes
        self.game_combo.bind('<<ComboboxSelected>>', self.on_game_changed)
        
        # Deck file selection
        deck_frame = ttk.LabelFrame(left_frame, text="  📂 Deck File  ", padding="8", style='TLabelframe')
        deck_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=5)
        deck_frame.columnconfigure(1, weight=1)
        
        deck_label = ttk.Label(deck_frame, text="Deck List:", style='Card.TLabel')
        deck_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        deck_entry = ttk.Entry(deck_frame, textvariable=self.deck_path, width=40, style='TEntry')
        deck_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        browse_btn = ttk.Button(deck_frame, text="Browse...", style='TButton')
        browse_btn.configure(command=self.browse_deck)
        browse_btn.grid(row=0, column=2)
        
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
        
        # Fetch button
        self.fetch_btn = ttk.Button(button_frame, text="🚀 Start Fetching Cards", 
                                     command=self.start_fetch, style='Accent.TButton')
        self.fetch_btn.pack(pady=5, ipadx=30, ipady=5)
        
        # Right column - Progress
        right_frame = ttk.Frame(parent, style='TFrame')
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        
        # Progress section
        progress_frame = ttk.LabelFrame(right_frame, text="  📊 Progress  ", padding="12", style='TLabelframe')
        progress_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(3, weight=1)
        
        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, mode='determinate', style='TProgressbar')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Progress label
        self.progress_label = ttk.Label(progress_frame, text="Ready to fetch cards", 
                                       font=('Segoe UI', 9), foreground='#808080',
                                       style='Card.TLabel')
        self.progress_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        # Current card preview - make it more prominent
        preview_container = ttk.Frame(progress_frame, style='TFrame')
        preview_container.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Card name label (larger, more visible)
        self.current_card_label = ttk.Label(preview_container, text="", 
                                           font=('Segoe UI', 12, 'bold'), 
                                           foreground='#4ec9b0',
                                           style='Card.TLabel',
                                           wraplength=700,
                                           justify=tk.LEFT)
        self.current_card_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Card details label (set, type, etc.)
        self.card_details_label = ttk.Label(preview_container, text="", 
                                           font=('Segoe UI', 9), 
                                           foreground='#9cdcfe',
                                           style='Card.TLabel',
                                           wraplength=700,
                                           justify=tk.LEFT)
        self.card_details_label.pack(anchor=tk.W)
        
        # Log text area with custom styling
        log_container = ttk.Frame(progress_frame, style='TFrame')
        log_container.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_container.columnconfigure(0, weight=1)
        log_container.rowconfigure(0, weight=1)
        
        self.progress_text = scrolledtext.ScrolledText(log_container, height=25, 
                                                        state='disabled', wrap=tk.WORD,
                                                        bg='#1e1e1e', fg='#d4d4d4',
                                                        font=('Consolas', 9),
                                                        relief='solid', borderwidth=1,
                                                        padx=10, pady=10,
                                                        insertbackground='#d4d4d4')
        self.progress_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags for colored output
        self.progress_text.tag_config('success', foreground='#4ec9b0')
        self.progress_text.tag_config('error', foreground='#f48771')
        self.progress_text.tag_config('info', foreground='#9cdcfe')
        self.progress_text.tag_config('warning', foreground='#dcdcaa')
        self.progress_text.tag_config('card', foreground='#4ec9b0', font=('Consolas', 9, 'bold'))
    
    def toggle_parallel(self):
        """Enable/disable parallel-related options based on checkbox"""
        state = 'normal' if self.parallel.get() else 'disabled'
        self.workers_spinbox.configure(state=state)
    
    def on_game_changed(self, event=None):
        """Update available formats and options when game selection changes"""
        # Get selected game name from combobox display
        game_display = self.game_combo.get()
        
        # Convert display name to ID
        game_id = self.game_name_to_id.get(game_display)
        if not game_id:
            return
        
        # Update the internal game ID variable
        self.selected_game.set(game_id)
        
        # Get plugin for selected game
        plugin = self.plugin_manager.get_plugin(game_id)
        if not plugin:
            return
        
        # Update available formats
        self.format_combo['values'] = plugin.deck_formats
        if plugin.deck_formats:
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
            if canvas.bbox('all') and canvas.bbox('all')[3] <= canvas.winfo_height():
                scrollbar.grid_remove()
            else:
                scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        left_frame.bind('<Configure>', on_pdf_frame_configure)
        
        canvas.create_window((0, 0), window=left_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Directory paths
        paths_frame = ttk.LabelFrame(left_frame, text="  📁 Directories  ", padding="8", style='TLabelframe')
        paths_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=5)
        paths_frame.columnconfigure(1, weight=1)
        
        # Front directory
        ttk.Label(paths_frame, text="Front Cards:", style='Card.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Entry(paths_frame, textvariable=self.front_dir, style='TEntry').grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=5)
        ttk.Button(paths_frame, text="Browse...", command=lambda: self.browse_directory(self.front_dir), style='TButton').grid(row=0, column=2, pady=5)
        
        # Back directory
        ttk.Label(paths_frame, text="Back Cards:", style='Card.TLabel').grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Entry(paths_frame, textvariable=self.back_dir, style='TEntry').grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=5)
        ttk.Button(paths_frame, text="Browse...", command=lambda: self.browse_directory(self.back_dir), style='TButton').grid(row=1, column=2, pady=5)
        
        # Double-sided directory
        ttk.Label(paths_frame, text="Double-Sided:", style='Card.TLabel').grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Entry(paths_frame, textvariable=self.double_sided_dir, style='TEntry').grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=5)
        ttk.Button(paths_frame, text="Browse...", command=lambda: self.browse_directory(self.double_sided_dir), style='TButton').grid(row=2, column=2, pady=5)
        
        # Output path
        ttk.Label(paths_frame, text="Output PDF:", style='Card.TLabel').grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Entry(paths_frame, textvariable=self.output_pdf_path, style='TEntry').grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=5)
        ttk.Button(paths_frame, text="Save As...", command=self.browse_pdf_output, style='TButton').grid(row=3, column=2, pady=5)
        
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
        
        # Offset Profile Selection
        ttk.Label(options_frame, text="Apply Offset Profile:", style='Card.TLabel').grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.pdf_profile_combo = ttk.Combobox(options_frame, textvariable=self.pdf_selected_profile, 
                                              state='readonly', style='TCombobox', width=30)
        self.pdf_profile_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        self.pdf_profile_combo.bind('<<ComboboxSelected>>', self.update_pdf_profile_info)
        
        # Add "None" option, legacy offset, and populate profiles
        profile_list = ["(None - No Offset)"]
        
        # Check if legacy offset exists
        legacy_offset = load_saved_offset()
        if legacy_offset:
            profile_list.append("(Legacy Saved Offset)")
        
        profile_list.extend(list_offset_profiles())
        self.pdf_profile_combo['values'] = profile_list
        
        # Try to set default profile
        profiles = load_offset_profiles()
        if profiles.default_profile and profiles.default_profile in profiles.profiles:
            self.pdf_selected_profile.set(profiles.default_profile)
        else:
            self.pdf_selected_profile.set("(None - No Offset)")
        
        # Profile info display
        self.pdf_profile_info_label = ttk.Label(options_frame, text="No offset will be applied", 
                                                style='Card.TLabel', font=('Segoe UI', 9), 
                                                foreground='#808080')
        self.pdf_profile_info_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(2, 10))
        self.update_pdf_profile_info()
        
        ttk.Label(options_frame, text="PDF Name Label:", style='Card.TLabel').grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Entry(options_frame, textvariable=self.pdf_name, width=30, style='TEntry').grid(row=3, column=1, sticky=tk.W, pady=5)
        
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
        
        self.pdf_progress_text = scrolledtext.ScrolledText(log_container, 
                                                          state='disabled', wrap=tk.WORD,
                                                          bg='#1e1e1e', fg='#d4d4d4',
                                                          font=('Consolas', 9),
                                                          relief='solid', borderwidth=1,
                                                          padx=10, pady=10)
        self.pdf_progress_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
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
            if canvas.bbox('all') and canvas.bbox('all')[3] <= canvas.winfo_height():
                scrollbar.grid_remove()
            else:
                scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        left_frame.bind('<Configure>', on_offset_frame_configure)
        
        canvas.create_window((0, 0), window=left_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Load saved offset or default profile on startup
        profiles = load_offset_profiles()
        if profiles.default_profile and profiles.default_profile in profiles.profiles:
            default_prof = profiles.profiles[profiles.default_profile]
            self.x_offset.set(default_prof.x_offset)
            self.y_offset.set(default_prof.y_offset)
            self.selected_profile.set(profiles.default_profile)
        else:
            saved = load_saved_offset()
            if saved:
                self.x_offset.set(saved.x_offset)
                self.y_offset.set(saved.y_offset)
        
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
        
        ttk.Button(new_profile_frame, text="💾 Save Current Settings as Profile", 
                  command=self.save_current_as_profile, style='Accent.TButton').grid(row=5, column=0, columnspan=2, pady=(10, 0))
        
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
        
        ttk.Label(offset_frame, text="PPI:", style='Card.TLabel').grid(row=5, column=0, sticky=tk.W, padx=(0, 10), pady=5)
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
                    "• Positive Y moves cards down, Negative Y moves up")
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
        
        self.offset_progress_text = scrolledtext.ScrolledText(progress_frame, 
                                                             state='disabled', wrap=tk.WORD,
                                                             bg='#1e1e1e', fg='#d4d4d4',
                                                             font=('Consolas', 9),
                                                             relief='solid', borderwidth=1,
                                                             padx=10, pady=10)
        self.offset_progress_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags
        self.offset_progress_text.tag_config('success', foreground='#4ec9b0')
        self.offset_progress_text.tag_config('error', foreground='#f48771')
        self.offset_progress_text.tag_config('info', foreground='#9cdcfe')
    
    def browse_directory(self, var):
        """Browse for a directory"""
        directory = filedialog.askdirectory(title="Select Directory")
        if directory:
            var.set(directory)
    
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
            self.deck_path.set(filename)
    
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
                self.update_profile_info()
                self.offset_log_message(f"📋 Loaded legacy saved offset")
            return
        
        # Handle named profiles
        profile = load_offset_profile(profile_name)
        if profile:
            self.x_offset.set(profile.x_offset)
            self.y_offset.set(profile.y_offset)
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
            description=description
        )
        
        # Clear form and refresh list
        self.profile_name.set("")
        self.profile_description.set("")
        self.refresh_profile_list()
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
        
        info_text = (f"{profile.description} | "
                    f"Paper: {profile.paper_size} | "
                    f"Offset: ({profile.x_offset}, {profile.y_offset})"
                    f"{default_text}")
        
        self.profile_info_label.config(text=info_text, foreground='#4ec9b0')
    
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
        
        info_text = (f"{profile.description} | "
                    f"Paper: {profile.paper_size} | "
                    f"Offset: ({profile.x_offset}, {profile.y_offset})"
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
        """Update progress bar (thread-safe)"""
        self.message_queue.put({'type': 'progress', 'current': current, 'total': total, 'text': text})
    
    def update_current_card(self, card_name, details=None):
        """Update currently processing card (thread-safe)"""
        self.message_queue.put({'type': 'card', 'card_name': card_name, 'details': details})
    
    def _update_current_card_internal(self, card_name, details=None):
        """Internal method to update current card (must be called from main thread)"""
        self.current_card_label.config(text=f"📥 Fetching: {card_name}")
        if details:
            self.card_details_label.config(text=details)
        else:
            self.card_details_label.config(text="")
    
    def _update_progress_internal(self, current, total, text=None):
        """Internal method to update progress (must be called from main thread)"""
        if total > 0:
            percentage = (current / total) * 100
            self.progress_var.set(percentage)
            
            if text:
                self.progress_label.config(text=text)
            else:
                self.progress_label.config(text=f"Processing: {current}/{total} cards ({percentage:.1f}%)")
    
    def validate_inputs(self):
        """Validate user inputs before starting fetch"""
        if not self.deck_path.get():
            messagebox.showerror("Error", "Please select a deck list file.")
            return False
        
        if not os.path.isfile(self.deck_path.get()):
            messagebox.showerror("Error", f"File not found: {self.deck_path.get()}")
            return False
        
        return True
    
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
        self.progress_var.set(0)
        self.progress_label.config(text="Initializing...")
        
        # Disable fetch button and update text
        self.fetch_btn.configure(state='disabled', text="⏳ Fetching...")
        self.is_fetching = True
        self.total_cards = 0
        self.completed_cards = 0
        
        # Run fetch in background thread
        thread = threading.Thread(target=self.fetch_cards, daemon=True)
        thread.start()
    
    def fetch_cards(self):
        """Fetch cards (runs in background thread)"""
        try:
            game_id = self.selected_game.get()
            plugin = self.plugin_manager.get_plugin(game_id)
            game_name = plugin.name if plugin else "Unknown Game"
            
            self.log_message("═" * 70, 'info')
            self.log_message(f"🎮 Game: {game_name}", 'info')
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
                
                # Set up directories
                front_directory = os.path.join('game', 'front')
                double_sided_directory = os.path.join('game', 'double_sided')
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
                        double_sided_directory
                    )
                    
                    # Read and parse deck
                    self.log_message("📖 Reading deck list...", 'info')
                    with open(self.deck_path.get(), 'r', encoding='utf-8') as deck_file:
                        deck_text = deck_file.read()
                        parse_deck(deck_text, format_enum, get_handle_card)
                    
                    # Process parallel downloads if enabled
                    if self.parallel.get() and hasattr(get_handle_card, 'download_queue'):
                        from plugins.mtg.download_manager import DownloadQueue
                        dl_queue = get_handle_card.download_queue
                        if dl_queue.size() > 0:
                            self.log_message("")
                            downloader = get_handle_card.downloader
                            downloader.download_cards_parallel(
                                tasks=dl_queue.get_all_tasks(),
                                fetch_function=get_handle_card.fetch_card_art,
                                front_dir=get_handle_card.front_img_dir,
                                double_sided_dir=get_handle_card.double_sided_dir,
                                art_crop=get_handle_card.art_crop
                            )
                
                elif game_id == "lorcana":
                    # Lorcana-specific handling
                    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'plugins', 'lorcana'))
                    from plugins.lorcana.deck_formats import DeckFormat as LorcanaDeckFormat
                    from plugins.lorcana.deck_formats import parse_dreamborn_list
                    from plugins.lorcana.lorcast import get_handle_card as lorcast_get_handle_card
                    
                    self.log_message("📖 Reading Lorcana deck list...", 'info')
                    with open(self.deck_path.get(), 'r', encoding='utf-8') as deck_file:
                        deck_text = deck_file.read()
                        parse_dreamborn_list(deck_text, lorcast_get_handle_card(front_directory))
                
                elif game_id == "yugioh":
                    # Yu-Gi-Oh! specific handling
                    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'plugins', 'yugioh'))
                    from plugins.yugioh.deck_formats import DeckFormat as YugiohDeckFormat, parse_deck as yugioh_parse
                    from plugins.yugioh.ygoprodeck import get_handle_card as yugioh_get_handle_card
                    
                    format_enum = YugiohDeckFormat(self.deck_format.get())
                    
                    self.log_message("📖 Reading Yu-Gi-Oh! deck list...", 'info')
                    with open(self.deck_path.get(), 'r', encoding='utf-8') as deck_file:
                        deck_text = deck_file.read()
                        yugioh_parse(deck_text, format_enum, yugioh_get_handle_card(front_directory))
                
                else:
                    # Generic handler for other plugins
                    self.log_message(f"⚠️ Plugin '{plugin.name}' is registered but fetch implementation is pending", 'warning')
                    self.log_message("📧 Please check the plugin documentation or implement the fetch function", 'info')
            finally:
                # Restore original print
                builtins.print = original_print
            
            self.log_message("")
            self.log_message("═" * 70, 'success')
            self.log_message("✅ All cards fetched successfully!", 'success')
            self.log_message("═" * 70, 'success')
            
            self.message_queue.put({'type': 'complete', 'success': True, 
                                   'message': 'Cards fetched successfully!'})
            
        except Exception as e:
            import traceback
            error_msg = str(e)
            self.log_message("")
            self.log_message("═" * 70, 'error')
            self.log_message(f"❌ ERROR: {error_msg}", 'error')
            self.log_message("═" * 70, 'error')
            
            # Log full traceback to console for debugging
            traceback.print_exc()
            
            self.message_queue.put({'type': 'complete', 'success': False, 'message': error_msg})
    
    def _fetch_complete_internal(self, success, message=None):
        """Called when fetch completes (must be called from main thread)"""
        # Clear current card preview
        self.current_card_label.config(text="")
        self.card_details_label.config(text="")
        
        # Re-enable fetch button
        self.fetch_btn.configure(state='normal', text='🚀 Start Fetching Cards')
        self.is_fetching = False
        
        if success:
            self.progress_var.set(100)
            self.progress_label.config(text="✅ Completed successfully!")
            messagebox.showinfo("Success", message or "Cards fetched successfully!")
        else:
            self.progress_label.config(text="❌ Error occurred")
            messagebox.showerror("Error", message or "An error occurred during fetch")
    
    def start_create_pdf(self):
        """Start PDF creation in background thread"""
        if self.is_creating_pdf:
            messagebox.showwarning("Warning", "PDF creation already in progress.")
            return
        
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
                    False,  # output_images
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
                    self.pdf_name.get() if self.pdf_name.get() else None
                )
                
                self.pdf_log_message("")
                self.pdf_log_message("═" * 70)
                self.pdf_log_message("✅ PDF created successfully!")
                self.pdf_log_message("═" * 70)
                
                self.root.after(0, lambda: self.pdf_creation_complete(True))
                
            finally:
                builtins.print = original_print
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.pdf_log_message("")
            self.pdf_log_message("═" * 70)
            self.pdf_log_message(f"❌ ERROR: {str(e)}")
            self.pdf_log_message("═" * 70)
            self.root.after(0, lambda: self.pdf_creation_complete(False, str(e)))
    
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
            messagebox.showinfo("Success", "PDF created successfully!")
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
                                            self.y_offset.get(), self.offset_ppi.get())
                
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
