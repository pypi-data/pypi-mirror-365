"""
Model Handler Mixin - Handles model loading and management
"""
from pathlib import Path
from PySide6.QtWidgets import QFileDialog, QMessageBox
from ..models.model_loader import ModelLoader, LLAMA_AVAILABLE


class ModelHandlerMixin:
    """Mixin class for handling model loading and management"""

    def load_model(self):
        """Load a GGUF model file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select GGUF Model File",
            "",
            "GGUF Files (*.gguf);;All Files (*)"
        )

        if not file_path:
            return

        if not LLAMA_AVAILABLE:
            QMessageBox.critical(
                self,
                "Missing Dependency",
                "llama-cpp-python is required but not installed.\n\n"
                "Install it with: pip install llama-cpp-python"
            )
            return

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.load_model_btn.setEnabled(False)
        self.status_label.setText("Loading model...")

        # Get settings
        use_gpu = self.processing_combo.currentText() == "GPU Accelerated"
        n_ctx = int(self.context_combo.currentText())

        # Start loading in thread
        self.model_loader = ModelLoader(file_path, use_gpu, n_ctx)
        self.model_loader.progress.connect(self.on_loading_progress)
        self.model_loader.finished.connect(self.on_model_loaded)
        self.model_loader.error.connect(self.on_loading_error)
        self.model_loader.start()

    def on_loading_progress(self, message: str):
        """Handle loading progress updates"""
        self.status_label.setText(message)

    def on_model_loaded(self, model):
        """Handle successful model loading"""
        self.model = model
        self.progress_bar.setVisible(False)
        self.load_model_btn.setEnabled(True)
        self.send_btn.setEnabled(True)

        model_name = Path(self.model_loader.model_path).name
        self.model_info.setText(f"✅ Loaded: {model_name}")
        self.status_label.setText("Model ready! Start chatting...")

        # Add system message
        self.add_system_message("🤖 AI Assistant loaded and ready to help!")
        
        # Emit signal for addon integration
        if hasattr(self, 'model_loaded'):
            self.model_loaded.emit(model)

    def on_loading_error(self, error_msg: str):
        """Handle model loading errors"""
        self.progress_bar.setVisible(False)
        self.load_model_btn.setEnabled(True)
        self.status_label.setText(f"❌ Error: {error_msg}")

        QMessageBox.critical(self, "Model Loading Error", error_msg)