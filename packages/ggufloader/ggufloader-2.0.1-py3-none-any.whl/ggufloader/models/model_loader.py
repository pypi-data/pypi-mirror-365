"""
Model loading functionality
"""
from PySide6.QtCore import QThread, Signal
from typing import Optional
from ..config import DEFAULT_CONTEXT_SIZES, DEFAULT_CONTEXT_INDEX

try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False


class ModelLoader(QThread):
    """Thread for loading GGUF models without blocking UI"""
    progress = Signal(str)  # Progress message
    finished = Signal(object)  # Loaded model or None
    error = Signal(str)  # Error message

    def __init__(self, model_path: str, use_gpu: bool, n_ctx: int = None):
        super().__init__()
        self.model_path = model_path
        self.use_gpu = use_gpu
        self.n_ctx = n_ctx or int(DEFAULT_CONTEXT_SIZES[DEFAULT_CONTEXT_INDEX])

    def run(self):
        try:
            self.progress.emit("Loading model...")

            if not LLAMA_AVAILABLE:
                self.error.emit("llama-cpp-python is not installed")
                return

            # Configure GPU layers
            n_gpu_layers = 20 if self.use_gpu else 0
            self.progress.emit(f"Initializing {'GPU' if self.use_gpu else 'CPU'} mode...")

            # Load the model
            model = Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_gpu_layers=n_gpu_layers,
                verbose=False
            )

            self.progress.emit("Model loaded successfully!")
            self.finished.emit(model)

        except Exception as e:
            self.error.emit(f"Failed to load model: {str(e)}")