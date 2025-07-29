"""
Addon Manager - Handles loading and managing addons for GGUF Loader
"""
import os
import sys
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, Optional, Callable, Any

from PySide6.QtWidgets import QWidget, QDialog, QVBoxLayout, QMessageBox
from PySide6.QtCore import Qt


class AddonManager:
    """Manages loading and registration of addons"""

    def __init__(self, addons_dir: str = "./addons"):
        self.addons_dir = Path(addons_dir)
        self.loaded_addons: Dict[str, Any] = {}
        self.addon_widgets: Dict[str, Callable] = {}
        self.addon_dialogs: Dict[str, QDialog] = {}
        self.addon_metadata: Dict[str, dict] = {}

    def scan_addons(self) -> Dict[str, str]:
        """Scan the addons directory and return available addons"""
        addons = {}

        if not self.addons_dir.exists():
            self.addons_dir.mkdir(parents=True, exist_ok=True)
            return addons

        for addon_path in self.addons_dir.iterdir():
            if addon_path.is_dir():
                init_file = addon_path / "__init__.py"
                if init_file.exists():
                    addons[addon_path.name] = str(init_file)

        return addons

    def load_addon(self, addon_name: str, addon_path: str) -> bool:
        """Load a single addon module"""
        try:
            # Create module spec
            spec = importlib.util.spec_from_file_location(
                f"addons.{addon_name}",
                addon_path
            )

            if spec is None or spec.loader is None:
                print(f"Failed to create spec for addon {addon_name}")
                return False

            # Load the module
            module = importlib.util.module_from_spec(spec)
            sys.modules[f"addons.{addon_name}"] = module
            spec.loader.exec_module(module)

            # Check if register function exists
            if hasattr(module, 'register'):
                self.loaded_addons[addon_name] = module
                self.addon_widgets[addon_name] = module.register

                # Load metadata if available
                if hasattr(module, 'get_metadata'):
                    try:
                        self.addon_metadata[addon_name] = module.get_metadata()
                    except Exception as e:
                        print(f"Failed to load metadata for addon {addon_name}: {e}")
                        self.addon_metadata[addon_name] = {}
                else:
                    self.addon_metadata[addon_name] = {}

                return True
            else:
                print(f"Addon {addon_name} missing register() function")

        except Exception as e:
            print(f"Failed to load addon {addon_name}: {e}")
            return False

        return False

    def unload_addon(self, addon_name: str) -> bool:
        """Unload a single addon"""
        try:
            # Close dialog if open
            if addon_name in self.addon_dialogs:
                self.addon_dialogs[addon_name].close()

            # Remove from loaded addons
            if addon_name in self.loaded_addons:
                # Call unload function if it exists
                if hasattr(self.loaded_addons[addon_name], 'unload'):
                    try:
                        self.loaded_addons[addon_name].unload()
                    except Exception as e:
                        print(f"Error during addon {addon_name} unload: {e}")

                del self.loaded_addons[addon_name]

            if addon_name in self.addon_widgets:
                del self.addon_widgets[addon_name]

            if addon_name in self.addon_metadata:
                del self.addon_metadata[addon_name]

            # Remove from sys.modules
            module_name = f"addons.{addon_name}"
            if module_name in sys.modules:
                del sys.modules[module_name]

            return True

        except Exception as e:
            print(f"Failed to unload addon {addon_name}: {e}")
            return False

    def load_all_addons(self) -> Dict[str, bool]:
        """Load all available addons"""
        results = {}
        addons = self.scan_addons()

        for addon_name, addon_path in addons.items():
            results[addon_name] = self.load_addon(addon_name, addon_path)

        return results

    def reload_addon(self, addon_name: str) -> bool:
        """Reload a specific addon"""
        if addon_name in self.loaded_addons:
            addon_path = None
            addons = self.scan_addons()
            if addon_name in addons:
                addon_path = addons[addon_name]

            if addon_path:
                self.unload_addon(addon_name)
                return self.load_addon(addon_name, addon_path)

        return False

    def get_addon_widget(self, addon_name: str, parent=None) -> Optional[QWidget]:
        """Get widget from addon's register function"""
        if addon_name in self.addon_widgets:
            try:
                return self.addon_widgets[addon_name](parent)
            except Exception as e:
                print(f"Error getting widget from addon {addon_name}: {e}")
                return None
        return None

    def open_addon_dialog(self, addon_name: str, parent=None):
        """Open addon in a dialog popup"""
        # Reuse existing dialog if open
        if addon_name in self.addon_dialogs:
            dialog = self.addon_dialogs[addon_name]
            if dialog.isVisible():
                dialog.raise_()
                dialog.activateWindow()
                return
            else:
                # Dialog was closed, remove from cache
                del self.addon_dialogs[addon_name]

        # Create new dialog
        widget = self.get_addon_widget(addon_name, parent)
        if widget is None:
            QMessageBox.warning(
                parent,
                "Addon Error",
                f"Failed to load addon '{addon_name}'"
            )
            return

        dialog = QDialog(parent)

        # Set dialog properties
        metadata = self.addon_metadata.get(addon_name, {})
        title = metadata.get('title', f"Addon: {addon_name}")
        dialog.setWindowTitle(title)

        dialog.setModal(False)  # Non-modal so main window stays accessible

        # Set dialog size
        width = metadata.get('width', 600)
        height = metadata.get('height', 400)
        dialog.resize(width, height)

        # Setup dialog layout
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widget)

        # Store dialog reference
        self.addon_dialogs[addon_name] = dialog

        # Clean up when dialog is closed
        def cleanup():
            if addon_name in self.addon_dialogs:
                del self.addon_dialogs[addon_name]

        dialog.finished.connect(cleanup)

        # Show dialog
        dialog.show()

    def get_loaded_addons(self) -> list:
        """Get list of successfully loaded addon names"""
        return list(self.loaded_addons.keys())

    def get_addon_metadata(self, addon_name: str) -> dict:
        """Get metadata for a specific addon"""
        return self.addon_metadata.get(addon_name, {})

    def is_addon_loaded(self, addon_name: str) -> bool:
        """Check if an addon is loaded"""
        return addon_name in self.loaded_addons

    def is_addon_dialog_open(self, addon_name: str) -> bool:
        """Check if an addon dialog is open"""
        return (addon_name in self.addon_dialogs and
                self.addon_dialogs[addon_name].isVisible())

    def close_addon_dialog(self, addon_name: str):
        """Close an addon dialog"""
        if addon_name in self.addon_dialogs:
            self.addon_dialogs[addon_name].close()

    def close_all_dialogs(self):
        """Close all addon dialogs"""
        for dialog in list(self.addon_dialogs.values()):
            dialog.close()