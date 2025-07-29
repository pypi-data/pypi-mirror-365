# GGUF Loader

[![PyPI version](https://badge.fury.io/py/ggufloader.svg)](https://badge.fury.io/py/ggufloader)
[![Python Support](https://img.shields.io/pypi/pyversions/ggufloader.svg)](https://pypi.org/project/ggufloader/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Advanced GGUF Model Loader with Smart Floating Assistant**

GGUF Loader is a production-ready Python application that provides a robust GGUF model loader with an innovative Smart Floating Assistant addon. Transform how you work with AI across all your applications with global text selection and processing capabilities.

## ✨ Key Features

### 🚀 Smart Floating Assistant
- **Global Text Selection**: Works across ALL applications (browsers, editors, documents)
- **AI-Powered Processing**: Summarize and comment on any selected text
- **Floating UI**: Non-intrusive, always-accessible interface
- **Privacy-First**: All processing happens locally on your machine

### 🎯 Core Capabilities
- **GGUF Model Support**: Load and run any GGUF format model
- **Modern GUI**: Built with PySide6 for a native desktop experience
- **Addon System**: Extensible architecture for custom functionality
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **GPU Acceleration**: Optional CUDA and Metal support

### 🔧 Developer-Friendly
- **Rich API**: Comprehensive addon development framework
- **Hot Loading**: Load and unload addons without restarting
- **Open Source**: MIT licensed and community-driven

## 🚀 Quick Start

### Installation

```bash
pip install ggufloader
```

### Launch

```bash
ggufloader
```

### First Steps

1. **Download a GGUF model** from [Hugging Face](https://huggingface.co/models?library=gguf)
2. **Click "Select GGUF Model"** in the application
3. **Load your model** and start chatting
4. **Try the Smart Assistant**: Select text anywhere and click the ✨ button!

## 📋 System Requirements

- **Python**: 3.8 or higher
- **RAM**: 4GB minimum (8GB+ recommended)
- **Storage**: 2GB+ free space for models
- **OS**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)

### Platform-Specific Requirements

#### Windows
- Windows 10 or 11
- Automatically installs `pywin32` for enhanced system integration

#### macOS
- macOS 10.14 (Mojave) or later
- Optional: Install enhanced macOS integration with `pip install ggufloader[macos]`

#### Linux
- Ubuntu 18.04+, Fedora 30+, or equivalent
- X11 display server (Wayland support coming soon)
- Optional: Install enhanced Linux integration with `pip install ggufloader[linux]`

## 🎮 Usage Examples

### Basic Chat
```python
# Launch the application
ggufloader

# Or use programmatically
from ggufloader import addon_main
addon_main()
```

### Smart Floating Assistant Workflow
1. **Reading an article** → Select key paragraph → Click ✨ → "Summarize"
2. **Code review** → Select complex function → Click ✨ → "Comment"  
3. **Email writing** → Select draft → Click ✨ → "Comment" for suggestions
4. **Research** → Select academic text → Click ✨ → "Summarize"

### Command Line Options
```bash
# Show version
ggufloader --version

# Show help
ggufloader --help
```

## 🔧 Advanced Installation

### GPU Acceleration

#### NVIDIA GPU (CUDA)
```bash
pip uninstall llama-cpp-python
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

#### Apple Silicon (Metal)
```bash
pip uninstall llama-cpp-python
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python
```

### Platform-Specific Enhanced Features

#### Windows Enhanced Integration
```bash
pip install ggufloader[windows]
```

#### macOS Enhanced Integration
```bash
pip install ggufloader[macos]
```

#### Linux Enhanced Integration
```bash
pip install ggufloader[linux]
```

### Performance Monitoring (Optional)
```bash
pip install ggufloader[performance]
```

### All Optional Features
```bash
pip install ggufloader[all]
```

### Development Installation
```bash
git clone https://github.com/GGUFloader/gguf-loader.git
cd gguf-loader
pip install -e .[dev]
```

## 📚 Documentation

### Quick Links
- **[Installation Guide](ggufloader/docs/installation.md)** - Detailed setup instructions
- **[Quick Start Guide](ggufloader/docs/quick-start.md)** - Get running in minutes  
- **[Addon Development](ggufloader/docs/addon-development.md)** - Create custom addons
- **[API Reference](ggufloader/docs/addon-api.md)** - Complete API documentation

### Key Documentation Files
- **[Package Structure](ggufloader/docs/package-structure.md)** - Understanding the codebase
- **[Smart Floater Example](ggufloader/docs/smart-floater-example.md)** - Learn from the built-in addon

## 🛠️ Development

### Project Structure
```
ggufloader/
├── __init__.py              # Package initialization
├── gguf_loader_main.py      # Main application entry point
├── addon_manager.py         # Addon system management
├── config.py               # Configuration utilities
├── addons/                 # Built-in addons
├── docs/                   # Documentation
├── models/                 # Model loading components
├── ui/                     # User interface components
└── widgets/                # Custom UI widgets
```

### Creating Addons

```python
# Example addon structure
def register_addon(parent_app):
    """Register addon with the main application"""
    return MyAddonWidget(parent_app)

class MyAddonWidget(QWidget):
    def __init__(self, parent_app):
        super().__init__()
        self.parent_app = parent_app
        # Your addon implementation
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Run tests**: `pytest`
5. **Submit a pull request**

### Development Setup
```bash
git clone https://github.com/GGUFloader/gguf-loader.git
cd gguf-loader
pip install -e .[dev]
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Homepage**: [https://ggufloader.github.io](https://ggufloader.github.io)
- **Repository**: [https://github.com/GGUFloader/gguf-loader](https://github.com/GGUFloader/gguf-loader)
- **PyPI Package**: [https://pypi.org/project/ggufloader/](https://pypi.org/project/ggufloader/)
- **Bug Reports**: [https://github.com/GGUFloader/gguf-loader/issues](https://github.com/GGUFloader/gguf-loader/issues)

## 👨‍💻 Author

**Hussain Nazary**
- Email: [hussainnazary475@gmail.com](mailto:hussainnazary475@gmail.com)
- GitHub: [@GGUFloader](https://github.com/GGUFloader)

## 🙏 Acknowledgments

- **llama.cpp** team for the excellent GGUF format and inference engine
- **PySide6** team for the robust GUI framework
- **Hugging Face** for model hosting and transformers library
- **Open source community** for continuous support and contributions

## 📊 Stats

- **Language**: Python 3.8+
- **GUI Framework**: PySide6
- **AI Backend**: llama-cpp-python
- **Package Size**: ~50MB
- **Supported Models**: All GGUF format models

---

**Transform your text workflow with AI-powered assistance! 🚀**

*Made with ❤️ by the GGUF Loader team*