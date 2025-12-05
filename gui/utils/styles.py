"""
UI Styles - Modern dark theme styling for the GUI
"""
from tkinter import ttk


class StyleManager:
    """Manages modern dark theme styles for the GUI"""
    
    # Color scheme
    BG_COLOR = '#1e1e1e'  # VS Code dark background
    CARD_BG = '#252526'  # Slightly lighter for cards
    TEXT_COLOR = '#d4d4d4'  # Light gray text
    ENTRY_BG = '#3c3c3c'  # Entry field background
    ENTRY_FG = '#ffffff'  # Entry field text - WHITE
    ACCENT_COLOR = '#0e639c'  # Blue accent
    ACCENT_HOVER = '#1177bb'  # Lighter blue on hover
    SUCCESS_COLOR = '#4ec9b0'  # Teal
    BORDER_COLOR = '#3e3e42'  # Subtle borders
    
    @staticmethod
    def setup_styles(root):
        """
        Configure modern, attractive styles
        
        Args:
            root: The Tkinter root window
        """
        # Configure root background
        root.configure(bg=StyleManager.BG_COLOR)
        
        # Use option_add for more reliable styling
        root.option_add('*TCombobox*Listbox.background', StyleManager.ENTRY_BG)
        root.option_add('*TCombobox*Listbox.foreground', StyleManager.ENTRY_FG)
        root.option_add('*TCombobox*Listbox.selectBackground', StyleManager.ACCENT_COLOR)
        root.option_add('*TCombobox*Listbox.selectForeground', StyleManager.ENTRY_FG)
        
        style = ttk.Style()
        
        # Use a modern theme as base
        try:
            style.theme_use('clam')  # Clam works better for customization
        except:
            pass
        
        StyleManager._configure_frame_styles(style)
        StyleManager._configure_button_styles(style)
        StyleManager._configure_input_styles(style)
        StyleManager._configure_other_styles(style)
    
    @staticmethod
    def _configure_frame_styles(style):
        """Configure frame and label styles"""
        style.configure('TFrame', background=StyleManager.BG_COLOR)
        style.configure('TLabel', background=StyleManager.BG_COLOR, font=('Segoe UI', 10), 
                       foreground=StyleManager.TEXT_COLOR)
        style.configure('Title.TLabel', font=('Segoe UI', 20, 'bold'), foreground='#ffffff', 
                       background=StyleManager.BG_COLOR)
        style.configure('Subtitle.TLabel', font=('Segoe UI', 9), foreground='#808080', 
                       background=StyleManager.BG_COLOR)
        style.configure('Card.TLabel', background=StyleManager.CARD_BG, font=('Segoe UI', 10), 
                       foreground=StyleManager.TEXT_COLOR)
        
        # LabelFrame styles
        style.configure('TLabelframe', background=StyleManager.CARD_BG, borderwidth=1, relief='solid')
        style.configure('TLabelframe.Label', background=StyleManager.CARD_BG, font=('Segoe UI', 10, 'bold'), 
                       foreground='#ffffff')
    
    @staticmethod
    def _configure_button_styles(style):
        """Configure button styles"""
        # Accent button (primary action - blue)
        style.configure('Accent.TButton', 
                       font=('Segoe UI', 12, 'bold'), 
                       padding=10,
                       background=StyleManager.ACCENT_COLOR,
                       foreground='#ffffff',
                       borderwidth=0)
        style.map('Accent.TButton', 
                 background=[('active', StyleManager.ACCENT_HOVER), ('pressed', StyleManager.ACCENT_COLOR), 
                            ('!active', StyleManager.ACCENT_COLOR)],
                 foreground=[('active', '#ffffff'), ('!active', '#ffffff'), ('disabled', '#808080')])
        
        # Regular buttons (small)
        style.configure('TButton', 
                       background='#3c3c3c', 
                       foreground='#ffffff',
                       borderwidth=1,
                       focuscolor='none',
                       font=('Segoe UI', 9))
        style.map('TButton',
                 background=[('active', '#4c4c4c'), ('pressed', '#2c2c2c'), ('!active', '#3c3c3c')],
                 foreground=[('!active', '#ffffff')])
        
        # Secondary button (large, gray)
        style.configure('Secondary.TButton',
                       font=('Segoe UI', 12, 'bold'),
                       padding=10,
                       background='#3c3c3c',
                       foreground='#ffffff',
                       borderwidth=0)
        style.map('Secondary.TButton',
                 background=[('active', '#4c4c4c'), ('pressed', '#2c2c2c'), ('!active', '#3c3c3c')],
                 foreground=[('!active', '#ffffff')])
        
        # Cancel button (large, red)
        style.configure('Cancel.TButton',
                       font=('Segoe UI', 12, 'bold'),
                       padding=10,
                       background='#d32f2f',
                       foreground='#ffffff',
                       borderwidth=0)
        style.map('Cancel.TButton',
                 background=[('active', '#b71c1c'), ('pressed', '#d32f2f'), ('!active', '#d32f2f'), 
                            ('disabled', '#5c5c5c')],
                 foreground=[('active', '#ffffff'), ('!active', '#ffffff'), ('disabled', '#808080')])
    
    @staticmethod
    def _configure_input_styles(style):
        """Configure input widget styles"""
        # Checkbutton
        style.configure('TCheckbutton', 
                       background=StyleManager.CARD_BG, 
                       font=('Segoe UI', 10), 
                       foreground=StyleManager.TEXT_COLOR,
                       focuscolor=StyleManager.CARD_BG)
        style.map('TCheckbutton',
                 background=[('active', StyleManager.CARD_BG)],
                 foreground=[('active', StyleManager.TEXT_COLOR)])
        
        # Entry
        style.configure('TEntry', 
                       fieldbackground=StyleManager.ENTRY_BG,
                       background=StyleManager.ENTRY_BG,
                       foreground=StyleManager.ENTRY_FG,
                       insertcolor=StyleManager.ENTRY_FG,
                       bordercolor=StyleManager.BORDER_COLOR,
                       lightcolor=StyleManager.BORDER_COLOR,
                       darkcolor=StyleManager.BORDER_COLOR)
        style.map('TEntry',
                 fieldbackground=[('readonly', StyleManager.ENTRY_BG), ('disabled', '#2c2c2c')],
                 foreground=[('readonly', StyleManager.ENTRY_FG), ('disabled', '#808080')])
        
        # Combobox
        style.configure('TCombobox',
                       fieldbackground=StyleManager.ENTRY_BG,
                       background=StyleManager.ENTRY_BG,
                       foreground=StyleManager.ENTRY_FG,
                       arrowcolor=StyleManager.ENTRY_FG,
                       bordercolor=StyleManager.BORDER_COLOR,
                       lightcolor=StyleManager.BORDER_COLOR,
                       darkcolor=StyleManager.BORDER_COLOR,
                       insertcolor=StyleManager.ENTRY_FG,
                       selectbackground=StyleManager.ACCENT_COLOR,
                       selectforeground=StyleManager.ENTRY_FG)
        style.map('TCombobox',
                 fieldbackground=[('readonly', StyleManager.ENTRY_BG), ('disabled', '#2c2c2c')],
                 foreground=[('readonly', StyleManager.ENTRY_FG), ('disabled', '#808080')],
                 selectbackground=[('readonly', StyleManager.ACCENT_COLOR)])
        
        # Spinbox
        style.configure('TSpinbox',
                       fieldbackground=StyleManager.ENTRY_BG,
                       background=StyleManager.ENTRY_BG,
                       foreground=StyleManager.ENTRY_FG,
                       arrowcolor=StyleManager.ENTRY_FG,
                       bordercolor=StyleManager.BORDER_COLOR,
                       insertcolor=StyleManager.ENTRY_FG)
        style.map('TSpinbox',
                 fieldbackground=[('readonly', StyleManager.ENTRY_BG), ('disabled', '#2c2c2c')],
                 foreground=[('readonly', StyleManager.ENTRY_FG), ('disabled', '#808080')])
    
    @staticmethod
    def _configure_other_styles(style):
        """Configure progressbar and notebook styles"""
        # Progressbar
        style.configure('TProgressbar', 
                       thickness=25, 
                       troughcolor='#3c3c3c', 
                       background=StyleManager.SUCCESS_COLOR,
                       bordercolor=StyleManager.BORDER_COLOR,
                       lightcolor=StyleManager.SUCCESS_COLOR,
                       darkcolor=StyleManager.SUCCESS_COLOR)
        
        # Notebook (tabs)
        style.configure('TNotebook', 
                       background=StyleManager.BG_COLOR,
                       borderwidth=0,
                       tabmargins=0)
        style.configure('TNotebook.Tab',
                       background='#2d2d2d',
                       foreground=StyleManager.TEXT_COLOR,
                       padding=[20, 12],
                       font=('Segoe UI', 10),
                       borderwidth=0,
                       focuscolor='none')
        style.map('TNotebook.Tab',
                 background=[('selected', StyleManager.CARD_BG), ('active', '#3c3c3c'), 
                            ('!selected', '#2d2d2d')],
                 foreground=[('selected', StyleManager.ACCENT_COLOR), ('active', StyleManager.TEXT_COLOR), 
                            ('!selected', StyleManager.TEXT_COLOR)],
                 padding=[('selected', [20, 12]), ('!selected', [20, 12])])
