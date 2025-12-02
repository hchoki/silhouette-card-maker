"""
MTG Card Fetcher - Graphical User Interface

A GUI for fetching Magic: The Gathering cards and creating PDFs without using the command line.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from pathlib import Path
import queue

# Add the project root to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'plugins', 'mtg'))

from deck_formats import DeckFormat
from scryfall import get_handle_card as scryfall_get_handle_card
from deck_formats import parse_deck
from utilities import Registration, CardSize, PaperSize, generate_pdf, load_saved_offset, save_offset


class MTGCardFetcherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MTG Card Fetcher & PDF Creator")
        self.root.geometry("950x1100")
        self.root.minsize(800, 900)
        
        # Message queue for thread-safe GUI updates
        self.message_queue = queue.Queue()
        
        # Configure modern style
        self.setup_styles()
        
        # Fetch card variables
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
        self.load_offset = tk.BooleanVar(value=False)
        self.pdf_name = tk.StringVar(value="")
        
        # Offset variables
        self.x_offset = tk.IntVar(value=0)
        self.y_offset = tk.IntVar(value=0)
        self.save_offset_flag = tk.BooleanVar(value=False)
        
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
        
        title_label = ttk.Label(header_frame, text="🃏 MTG Card Fetcher & PDF Creator", 
                               font=('Segoe UI', 20, 'bold'), 
                               foreground='#ffffff',
                               style='Card.TLabel')
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        subtitle_label = ttk.Label(header_frame, text="Download Magic: The Gathering cards for proxy printing", 
                                  font=('Segoe UI', 10), 
                                  foreground='#a0a0a0',
                                  style='Card.TLabel')
        subtitle_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(main_frame, style='TNotebook')
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        
        # Tab 1: Fetch Cards
        fetch_tab = ttk.Frame(self.notebook, style='TFrame', padding="15")
        self.notebook.add(fetch_tab, text='  📥 Fetch Cards  ')
        self.setup_fetch_tab(fetch_tab)
        
        # Tab 2: Create PDF
        pdf_tab = ttk.Frame(self.notebook, style='TFrame', padding="15")
        self.notebook.add(pdf_tab, text='  📄 Create PDF  ')
        self.setup_pdf_tab(pdf_tab)
        
        # Tab 3: Offset PDF
        offset_tab = ttk.Frame(self.notebook, style='TFrame', padding="15")
        self.notebook.add(offset_tab, text='  ⚙️ Offset PDF  ')
        self.setup_offset_tab(offset_tab)
    
    def setup_fetch_tab(self, parent):
        """Setup the card fetching tab"""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(4, weight=1)
        
        # Deck file selection
        deck_frame = ttk.LabelFrame(parent, text="  📂 Deck File  ", padding="12", style='TLabelframe')
        deck_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 12))
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
        format_combo = ttk.Combobox(deck_frame, textvariable=self.deck_format, 
                                     values=['archidekt', 'moxfield', 'deckstats', 'tappedout', 'generic'], 
                                     state='readonly', width=20, style='TCombobox')
        format_combo.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        # Basic options
        basic_frame = ttk.LabelFrame(parent, text="  ⚙️ Basic Options  ", padding="12", style='TLabelframe')
        basic_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 12))
        
        ttk.Checkbutton(basic_frame, text="Download Art Crop (for Proxyshop)", 
                        variable=self.art_crop).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(basic_frame, text="Fetch Related Tokens", 
                        variable=self.tokens).grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(basic_frame, text="Ignore Set & Collector Number", 
                        variable=self.ignore_set_collector).grid(row=2, column=0, sticky=tk.W, pady=2)
        
        # Card preferences
        pref_frame = ttk.LabelFrame(parent, text="  🎨 Card Preferences  ", padding="12", style='TLabelframe')
        pref_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 12))
        
        ttk.Checkbutton(pref_frame, text="Prefer Showcase Cards", 
                        variable=self.prefer_showcase).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(pref_frame, text="Prefer Full Art / Borderless / Extended Art", 
                        variable=self.prefer_extra_art).grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(pref_frame, text="Prefer Older Sets", 
                        variable=self.prefer_older_sets).grid(row=2, column=0, sticky=tk.W, pady=2)
        
        # Performance options
        perf_frame = ttk.LabelFrame(parent, text="  🚀 Performance Settings  ", padding="12", style='TLabelframe')
        perf_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 12))
        
        ttk.Checkbutton(perf_frame, text="Enable Parallel Downloads", 
                        variable=self.parallel, command=self.toggle_parallel).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        ttk.Label(perf_frame, text="Max Workers:", style='Card.TLabel').grid(row=1, column=0, sticky=tk.W, padx=(20, 10), pady=5)
        self.workers_spinbox = ttk.Spinbox(perf_frame, from_=1, to=20, textvariable=self.max_workers, 
                                          width=10, style='TSpinbox')
        self.workers_spinbox.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(perf_frame, text="API Delay (seconds):", style='Card.TLabel').grid(row=2, column=0, sticky=tk.W, padx=(20, 10), pady=5)
        delay_spinbox = ttk.Spinbox(perf_frame, from_=0.01, to=0.5, increment=0.01, 
                                     textvariable=self.api_delay, width=10, format="%.2f", style='TSpinbox')
        delay_spinbox.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(perf_frame, text="(Lower = faster, but respect Scryfall's limits)", 
                  font=('Segoe UI', 8), foreground='#808080', style='Card.TLabel').grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=(20, 0))
        
        # Progress section
        progress_frame = ttk.LabelFrame(parent, text="  📊 Progress  ", padding="12", style='TLabelframe')
        progress_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 12))
        parent.rowconfigure(4, weight=1)
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
        
        self.progress_text = scrolledtext.ScrolledText(log_container, height=30, width=100, 
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
        
        # Button frame
        button_frame = ttk.Frame(parent, style='TFrame')
        button_frame.grid(row=5, column=0, columnspan=3, pady=(12, 0))
        
        # Fetch button
        self.fetch_btn = ttk.Button(button_frame, text="🚀 Start Fetching Cards", 
                                     command=self.start_fetch, style='Accent.TButton')
        self.fetch_btn.pack(pady=5, ipadx=30, ipady=5)
        
    def toggle_parallel(self):
        """Enable/disable parallel-related options based on checkbox"""
        state = 'normal' if self.parallel.get() else 'disabled'
        self.workers_spinbox.configure(state=state)
    
    def setup_pdf_tab(self, parent):
        """Setup the PDF creation tab"""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(6, weight=1)
        
        # Directory paths
        paths_frame = ttk.LabelFrame(parent, text="  📁 Directories  ", padding="12", style='TLabelframe')
        paths_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 12))
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
        size_frame = ttk.LabelFrame(parent, text="  📏 Size Settings  ", padding="12", style='TLabelframe')
        size_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 12))
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
        options_frame = ttk.LabelFrame(parent, text="  ⚙️ PDF Options  ", padding="12", style='TLabelframe')
        options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 12))
        options_frame.columnconfigure(1, weight=1)
        
        ttk.Checkbutton(options_frame, text="Only Fronts (exclude backs)", 
                       variable=self.only_fronts).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Load Saved Offset", 
                       variable=self.load_offset).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        ttk.Label(options_frame, text="Crop Amount:", style='Card.TLabel').grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Entry(options_frame, textvariable=self.crop_amount, width=15, style='TEntry').grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Label(options_frame, text="(e.g., 3mm, 0.125in, 6.5)", 
                 font=('Segoe UI', 8), foreground='#808080', style='Card.TLabel').grid(row=3, column=0, columnspan=2, sticky=tk.W)
        
        ttk.Label(options_frame, text="PDF Name Label:", style='Card.TLabel').grid(row=4, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Entry(options_frame, textvariable=self.pdf_name, width=30, style='TEntry').grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Advanced options
        advanced_frame = ttk.LabelFrame(parent, text="  🔧 Advanced  ", padding="12", style='TLabelframe')
        advanced_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 12))
        advanced_frame.columnconfigure(1, weight=1)
        
        ttk.Label(advanced_frame, text="Extend Corners:", style='Card.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Spinbox(advanced_frame, from_=0, to=100, textvariable=self.extend_corners, 
                   width=10, style='TSpinbox').grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(advanced_frame, text="PPI (Resolution):", style='Card.TLabel').grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Spinbox(advanced_frame, from_=72, to=600, textvariable=self.ppi, 
                   width=10, style='TSpinbox').grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(advanced_frame, text="Quality (0-100):", style='Card.TLabel').grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Spinbox(advanced_frame, from_=1, to=100, textvariable=self.pdf_quality, 
                   width=10, style='TSpinbox').grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Progress area (shared)
        progress_frame = ttk.LabelFrame(parent, text="  📊 Progress  ", padding="12", style='TLabelframe')
        progress_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 12))
        parent.rowconfigure(4, weight=1)
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(0, weight=1)
        
        self.pdf_progress_text = scrolledtext.ScrolledText(progress_frame, height=20, width=100, 
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
        
        # Create button
        button_frame = ttk.Frame(parent, style='TFrame')
        button_frame.grid(row=5, column=0, pady=(12, 0))
        
        self.create_pdf_btn = ttk.Button(button_frame, text="📄 Create PDF", 
                                        command=self.start_create_pdf, style='Accent.TButton')
        self.create_pdf_btn.pack(pady=5, ipadx=30, ipady=5)
    
    def setup_offset_tab(self, parent):
        """Setup the PDF offset tab"""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(3, weight=1)
        
        # Load saved offset on startup
        saved = load_saved_offset()
        if saved:
            self.x_offset.set(saved.x_offset)
            self.y_offset.set(saved.y_offset)
        
        # Offset settings
        offset_frame = ttk.LabelFrame(parent, text="  ⚙️ Offset Settings  ", padding="12", style='TLabelframe')
        offset_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 12))
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
        
        ttk.Checkbutton(offset_frame, text="Save these offset values for future use", 
                       variable=self.save_offset_flag).grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(10, 2))
        
        # Info panel
        info_frame = ttk.LabelFrame(parent, text="  ℹ️ Information  ", padding="12", style='TLabelframe')
        info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 12))
        
        info_text = ("Offset your PDF if your printer has registration issues.\n\n"
                    "• Positive X offset moves cards right\n"
                    "• Negative X offset moves cards left\n"
                    "• Positive Y offset moves cards down\n"
                    "• Negative Y offset moves cards up\n\n"
                    "Saved offsets are automatically loaded and can be applied during PDF creation.")
        ttk.Label(info_frame, text=info_text, style='Card.TLabel', 
                 font=('Segoe UI', 9), foreground='#a0a0a0', justify=tk.LEFT).pack(anchor=tk.W)
        
        # Progress area
        progress_frame = ttk.LabelFrame(parent, text="  📊 Progress  ", padding="12", style='TLabelframe')
        progress_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 12))
        parent.rowconfigure(2, weight=1)
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(0, weight=1)
        
        self.offset_progress_text = scrolledtext.ScrolledText(progress_frame, height=15, width=100, 
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
        
        # Apply button
        button_frame = ttk.Frame(parent, style='TFrame')
        button_frame.grid(row=3, column=0, pady=(12, 0))
        
        self.apply_offset_btn = ttk.Button(button_frame, text="⚙️ Apply Offset", 
                                          command=self.start_apply_offset, style='Accent.TButton')
        self.apply_offset_btn.pack(pady=5, ipadx=30, ipady=5)
    
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
            self.log_message("═" * 70, 'info')
            self.log_message(f"📄 Deck: {os.path.basename(self.deck_path.get())}", 'info')
            self.log_message(f"📋 Format: {self.deck_format.get()}", 'info')
            self.log_message(f"🎨 Art Crop: {'Yes' if self.art_crop.get() else 'No'}", 'info')
            self.log_message(f"🪙 Tokens: {'Yes' if self.tokens.get() else 'No'}", 'info')
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
                # Set up directories
                front_directory = os.path.join('game', 'front')
                double_sided_directory = os.path.join('game', 'double_sided')
                os.makedirs(front_directory, exist_ok=True)
                os.makedirs(double_sided_directory, exist_ok=True)
                
                # Get the fetch function
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
                    self.load_offset.get(),
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
                self.offset_log_message("═" * 70)
                self.offset_log_message("")
                
                # Save offset if requested
                if self.save_offset_flag.get():
                    save_offset(self.x_offset.get(), self.y_offset.get())
                    self.offset_log_message("💾 Offset values saved for future use")
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
