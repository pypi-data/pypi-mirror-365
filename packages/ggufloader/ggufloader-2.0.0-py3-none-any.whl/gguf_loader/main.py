#!/usr/bin/env python3
"""
Main entry point for the Advanced Local AI Chat Application
"""
import os
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from .models.model_loader import ModelLoader
from .utils import load_fonts
from .ui.ai_chat_window import AIChat
from .resource_manager import find_icon, get_dll_path

def add_dll_folder():
    """Add DLL directory for llama.cpp when needed."""
    dll_path = get_dll_path()
    if dll_path and os.path.exists(dll_path):
        os.add_dll_directory(dll_path)

def main():
    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--version', '-v']:
            from . import __version__
            print(f"GGUF Loader Basic version {__version__}")
            return
        elif sys.argv[1] in ['--help', '-h']:
            print("GGUF Loader Basic - Simple GGUF Model Loader")
            print("\nUsage: ggufloader-basic [options]")
            print("\nOptions:")
            print("  --version, -v    Show version information")
            print("  --help, -h       Show this help message")
            return

    add_dll_folder()

    app = QApplication(sys.argv)

    # Set application icon for taskbar & alt-tab
    icon_path = find_icon("icon.ico")
    print(f"[DEBUG] Loading icon from: {icon_path}")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    else:
        print(f"[WARNING] Icon not found at: {icon_path}")

    # Load fonts
    load_fonts()

    # Create and show main window
    window = AIChat()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
