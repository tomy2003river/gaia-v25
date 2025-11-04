"""
Tkinter UI for GAIA v25.
Non-blocking interface with threaded message processing.
"""
import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import logging
from typing import Optional

from gaia import GAIACore
from config import Config
from core import setup_logging

logger = logging.getLogger(__name__)


class GAIAUI:
    """Tkinter-based UI for GAIA."""
    
    def __init__(self, root: tk.Tk, gaia_core: GAIACore):
        """
        Initialize UI.
        
        Args:
            root: Tkinter root window
            gaia_core: GAIA core instance
        """
        self.root = root
        self.gaia = gaia_core
        self.processing = False
        
        self.root.title("GAIA v25 - Asistente Multimodal")
        self.root.geometry("800x600")
        
        self._create_widgets()
        self._setup_styles()
        
        # Welcome message
        self._add_message("GAIA", "¡Hola! Soy GAIA, tu asistente multimodal. ¿En qué puedo ayudarte?")
    
    def _create_widgets(self):
        """Create UI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="GAIA v25",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Chat display
        chat_frame = ttk.Frame(main_frame)
        chat_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            width=80,
            height=25,
            font=("Arial", 10),
            state=tk.DISABLED
        )
        self.chat_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        input_frame.columnconfigure(0, weight=1)
        
        self.input_entry = ttk.Entry(input_frame, font=("Arial", 10))
        self.input_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.input_entry.bind("<Return>", lambda e: self._send_message())
        self.input_entry.focus()
        
        self.send_button = ttk.Button(
            input_frame,
            text="Enviar",
            command=self._send_message
        )
        self.send_button.grid(row=0, column=1)
        
        # Status bar
        self.status_var = tk.StringVar(value="Listo")
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
    
    def _setup_styles(self):
        """Setup text tags for styling."""
        self.chat_display.tag_config("user", foreground="#2196F3", font=("Arial", 10, "bold"))
        self.chat_display.tag_config("gaia", foreground="#4CAF50", font=("Arial", 10, "bold"))
        self.chat_display.tag_config("error", foreground="#F44336", font=("Arial", 10, "italic"))
        self.chat_display.tag_config("system", foreground="#757575", font=("Arial", 9, "italic"))
    
    def _add_message(self, sender: str, message: str, tag: Optional[str] = None):
        """
        Add message to chat display.
        
        Args:
            sender: Message sender
            message: Message text
            tag: Optional text tag for styling
        """
        self.chat_display.config(state=tk.NORMAL)
        
        # Add sender
        sender_tag = "user" if sender == "Tú" else "gaia"
        self.chat_display.insert(tk.END, f"{sender}: ", sender_tag)
        
        # Add message
        msg_tag = tag or "system"
        self.chat_display.insert(tk.END, f"{message}\n\n", msg_tag if tag else None)
        
        # Scroll to end
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def _send_message(self):
        """Handle send button click."""
        if self.processing:
            return
        
        message = self.input_entry.get().strip()
        if not message:
            return
        
        # Clear input
        self.input_entry.delete(0, tk.END)
        
        # Show user message
        self._add_message("Tú", message)
        
        # Set processing state
        self.processing = True
        self.status_var.set("Procesando...")
        self.send_button.config(state=tk.DISABLED)
        self.input_entry.config(state=tk.DISABLED)
        
        # Process in background thread
        thread = threading.Thread(
            target=self._process_message_thread,
            args=(message,),
            daemon=True
        )
        thread.start()
    
    def _process_message_thread(self, message: str):
        """
        Process message in background thread.
        
        Args:
            message: User message
        """
        try:
            # Process message
            response = self.gaia.process_message(message, speak=True)
            
            # Update UI (must be done on main thread)
            self.root.after(0, self._show_response, response)
            
        except Exception as e:
            logger.error(f"Error in message thread: {e}", exc_info=True)
            self.root.after(0, self._show_error, str(e))
    
    def _show_response(self, response):
        """
        Show response in UI (main thread).
        
        Args:
            response: Response object
        """
        # Show response
        tag = None if response.success else "error"
        self._add_message("GAIA", response.text, tag=tag)
        
        # Reset state
        self.processing = False
        self.status_var.set("Listo")
        self.send_button.config(state=tk.NORMAL)
        self.input_entry.config(state=tk.NORMAL)
        self.input_entry.focus()
    
    def _show_error(self, error: str):
        """
        Show error in UI (main thread).
        
        Args:
            error: Error message
        """
        self._add_message("Sistema", f"Error: {error}", tag="error")
        
        # Reset state
        self.processing = False
        self.status_var.set("Error")
        self.send_button.config(state=tk.NORMAL)
        self.input_entry.config(state=tk.NORMAL)
        self.input_entry.focus()
    
    def run(self):
        """Start the UI main loop."""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()
    
    def _on_closing(self):
        """Handle window closing."""
        logger.info("Closing GAIA UI")
        self.gaia.shutdown()
        self.root.destroy()


def main():
    """Main entry point."""
    # Setup logging
    setup_logging(
        log_level=Config.GAIA_LOG_LEVEL,
        log_file=Config.LOGS_DIR / Config.GAIA_LOG_FILE
    )
    
    logger.info("Starting GAIA v25...")
    
    # Validate configuration
    valid, errors = Config.validate()
    if not valid:
        print("❌ Error de configuración:")
        for error in errors:
            print(f"  - {error}")
        print("\nPor favor, configura el archivo .env siguiendo .env.example")
        return
    
    # Show configuration
    print("✓ GAIA v25 - Configuración cargada")
    summary = Config.get_summary()
    print(f"  • Ciudad: {summary['city']}")
    print(f"  • Idioma: {summary['lang']}")
    print(f"  • API Key configurada: {'Sí' if summary['api_key_set'] else 'No'}")
    print()
    
    # Initialize GAIA
    try:
        gaia_core = GAIACore(Config)
        
        # Create and run UI
        root = tk.Tk()
        ui = GAIAUI(root, gaia_core)
        ui.run()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Error fatal: {e}")
        return


if __name__ == "__main__":
    main()
