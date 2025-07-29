# Video Edit MCP Server 🎬

A powerful **Model Context Protocol (MCP) server** for video editing operations using MoviePy. This server enables AI assistants to perform comprehensive video editing tasks through a standardized interface.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![MoviePy](https://img.shields.io/badge/MoviePy-1.0.3-green.svg)
![MCP](https://img.shields.io/badge/MCP-Compatible-purple.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🚀 Features

### Core Video Operations
- **🎯 Video Trimming**: Extract specific time ranges from videos
- **🔗 Video Concatenation**: Join multiple videos seamlessly  
- **✂️ Video Splitting**: Split videos into multiple segments
- **⚡ Speed Control**: Speed up or slow down video playback
- **🔄 Video Reversal**: Play videos backwards
- **🔄 Video Rotation**: Rotate videos by any angle

### Audio Processing
- **🎵 Audio Extraction**: Extract audio tracks from videos
- **🔊 Audio Replacement**: Replace video soundtracks
- **📢 Volume Control**: Adjust audio volume levels
- **🎚️ Audio Synchronization**: Automatically match audio/video durations

### Advanced Features
- **💾 In-Memory Processing**: Efficient reference-based video manipulation
- **📁 Batch Operations**: Process multiple videos simultaneously  
- **🧹 Resource Management**: Automatic cleanup to prevent memory leaks
- **📊 Media Information**: Detailed video/audio metadata extraction
- **✅ Error Handling**: Comprehensive error reporting and validation

## 📋 Requirements

- Python 3.8+
- MoviePy 1.0.3
- Model Context Protocol Python SDK
- FFmpeg (for video processing)

## ⚙️ Installation

### Quick Install (Recommended)

**Install directly with uvx for instant use** (once published to PyPI):
```bash
uvx video-edit-mcp
```

> **Note**: Package will be available on PyPI soon. For now, use manual installation.

### For MCP Client Integration

Add this to your MCP client configuration file (e.g., Claude Desktop config):

```json
{
    "tools": {
        "video-edit": {
            "command": "uvx",
            "args": [
                "video-edit-mcp"
            ]
        }
    }
}
```

**For Claude Desktop users**, edit your configuration file located at:
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Manual Installation

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/video-edit-mcp.git
cd video-edit-mcp
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Install the package**:
```bash
pip install -e .
```

### Prerequisites

**Ensure FFmpeg is installed** (required for video processing):
```bash
# On Windows (using chocolatey)
choco install ffmpeg

# On macOS (using homebrew)  
brew install ffmpeg

# On Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg
```

## 🎯 Usage

### Running the MCP Server

The server can be integrated with any MCP-compatible client:

```python
from mcp.server.fastmcp import FastMCP

# The server is automatically configured and ready to use
# Tools are registered and available for AI assistants
```

### Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_video_info` | Get comprehensive video metadata | `video_ref` |
| `get_audio_info` | Get detailed audio information | `audio_ref` |
| `trim_video` | Extract video segments | `video_ref, start_time, end_time, save, name_of_video` |
| `concatenate_videos` | Join multiple videos | `video_refs[], save, name_of_video` |
| `split_video` | Split into multiple segments | `video_ref, timestamps[], save, name_of_video` |
| `speed_up_or_slow_down_video` | Change playback speed | `video_ref, speed_factor, save, name_of_video` |
| `reverse_video` | Play video backwards | `video_ref, save, name_of_video` |
| `rotate_video` | Rotate by degrees | `video_ref, angle, save, name_of_video` |
| `extract_audio` | Extract audio track | `video_ref, save, name_of_audio` |
| `audio_replacement` | Replace video audio | `video_ref, audio_ref, save, fps, name_of_video` |
| `volume_control` | Adjust audio volume | `video_ref, volume_factor, save, name_of_video` |
| `cleanup_resources` | Free memory resources | `video_refs[], audio_refs[]` |

### Example Workflow

```python
# 1. Get video information
info = get_video_info("path/to/video.mp4")

# 2. Trim video to 30 seconds
trimmed_ref = trim_video("path/to/video.mp4", 0, 30, save=False)

# 3. Speed up the trimmed video 2x
fast_ref = speed_up_or_slow_down_video(trimmed_ref["video_ref"], 2.0, save=False)

# 4. Save final result
final_video = speed_up_or_slow_down_video(fast_ref["video_ref"], 1.0, save=True, name_of_video="final_edit")
```

## 🏗️ Project Structure

```
video_edit_mcp/
├── main.py              # Main MCP server implementation
├── requirements.txt     # Python dependencies
├── pyproject.toml      # Project configuration
├── README.md           # This file
├── video_store/        # Output directory for processed videos
└── test.py            # Test utilities
```

## 🎛️ Configuration

### Memory Management
- Videos are stored in-memory using UUID references for efficient processing
- Use `cleanup_resources()` to prevent memory leaks during batch operations
- Large videos are automatically handled with streaming where possible

### Output Settings  
- Default output format: MP4 with H.264 encoding
- Custom FPS settings available for audio replacement operations
- Automatic quality optimization based on input video properties

## 🔮 Planned Features & Enhancements

### 🎨 Visual Effects
- [ ] **Color Correction**: Brightness, contrast, saturation adjustments
- [ ] **Filters & Effects**: Blur, sharpen, vintage, sepia effects
- [ ] **Transitions**: Fade in/out, crossfade, wipe transitions
- [ ] **Text Overlays**: Dynamic text with custom fonts and animations
- [ ] **Image Overlays**: Watermarks, logos, picture-in-picture

### 🎵 Advanced Audio
- [ ] **Audio Mixing**: Combine multiple audio tracks
- [ ] **Noise Reduction**: AI-powered audio cleanup
- [ ] **Audio Effects**: Echo, reverb, equalization
- [ ] **Voice Processing**: Pitch shifting, voice enhancement
- [ ] **Music Generation**: AI-generated background music

### 🧠 AI-Powered Features
- [ ] **Smart Cropping**: Automatic scene detection and cropping
- [ ] **Object Tracking**: Follow subjects throughout the video
- [ ] **Scene Detection**: Automatic chapter/scene identification
- [ ] **Content Analysis**: Automatic tagging and categorization
- [ ] **Quality Enhancement**: AI upscaling and noise reduction

### 🔧 Technical Improvements
- [ ] **GPU Acceleration**: CUDA/OpenCL support for faster processing
- [ ] **Streaming Support**: Handle large files without loading into memory
- [ ] **Format Support**: WebM, AVI, MOV, and more format options
- [ ] **Cloud Integration**: AWS S3, Google Cloud Storage support
- [ ] **Progress Tracking**: Real-time processing progress updates

### 🌐 Integration & API
- [ ] **REST API**: HTTP endpoints for web integration
- [ ] **WebSocket Support**: Real-time communication for live editing
- [ ] **Plugin System**: Extensible architecture for custom effects
- [ ] **CLI Interface**: Command-line tools for batch processing
- [ ] **Docker Support**: Containerized deployment options

### 📊 Analytics & Monitoring
- [ ] **Performance Metrics**: Processing time and resource usage tracking
- [ ] **Quality Metrics**: Automatic video quality assessment
- [ ] **Usage Analytics**: Tool usage statistics and optimization suggestions
- [ ] **Error Reporting**: Detailed error tracking and debugging tools

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/video-edit-mcp.git
cd video-edit-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Install in development mode
pip install -e .

# Run tests
pytest test.py
```

### Publishing to PyPI

To make your server available via `uvx` like the OpenCV example:

```bash
# Build the package
python -m build

# Upload to PyPI (requires account and API token)
python -m twine upload dist/*
```

After publishing, users can install with:
```bash
uvx video-edit-mcp
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[MoviePy](https://zulko.github.io/moviepy/)** - The amazing video editing library powering this project
- **[Model Context Protocol](https://github.com/modelcontextprotocol/python-sdk)** - For the standardized AI integration framework
- **[FFmpeg](https://ffmpeg.org/)** - The multimedia framework behind MoviePy

## 📞 Support

- 🐛 **Bug Reports**: [Create an issue](https://github.com/yourusername/video-edit-mcp/issues)
- 💡 **Feature Requests**: [Start a discussion](https://github.com/yourusername/video-edit-mcp/discussions)
- 📧 **Email**: your.email@example.com
- 💬 **Discord**: [Join our community](https://discord.gg/yourserver)

---

<div align="center">

**Made with ❤️ for the AI and video editing community**

[⭐ Star this project](https://github.com/yourusername/video-edit-mcp) | [🍴 Fork it](https://github.com/yourusername/video-edit-mcp/fork) | [📢 Share it](https://twitter.com/intent/tweet?text=Check%20out%20this%20amazing%20Video%20Edit%20MCP%20Server!%20https://github.com/yourusername/video-edit-mcp)

</div>
