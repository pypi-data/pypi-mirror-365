# PysvgGenius

An intelligent SVG optimization library that uses machine learning to enhance SVG quality through aesthetic evaluation, similarity matching, and differential vector graphics optimization.

## 🚀 Features

- **Aesthetic Enhancement**: Uses CLIP-based models to improve visual appeal
- **Similarity Matching**: SIGLIP model for text-image similarity optimization  
- **Differential Optimization**: DiffVG for gradient-based SVG parameter tuning
- **Multiple Generators**: Support for SDXL-Turbo and Stable Diffusion models
- **Vector Conversion**: VTracer integration for raster-to-vector conversion
- **Flexible Architecture**: Modular design with factory patterns

## 📋 Prerequisites

- **Python**: 3.8 or higher
- **CUDA**: Compatible GPU with CUDA support (recommended)
- **Git**: For cloning dependencies
- **Build Tools**: GCC/Clang compiler, CMake

### System Dependencies

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y build-essential cmake git python3-dev
sudo apt install -y libcairo2-dev pkg-config python3-dev
```

#### macOS
```bash
brew install cmake git cairo pkg-config
xcode-select --install
```

## 🔧 Installation

### Option 1: Quick Install (Recommended)

```bash
# Clone the repository
git clone https://github.com/tamchamchi/pysvgenius.git
cd pysvgenius

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with automatic diffvg setup
pip install -e .
```

### Option 2: Manual Installation

If you prefer to install dependencies step by step:

```bash
# 1. Clone repository
git clone https://github.com/tamchamchi/pysvgenius.git
cd pysvgenius

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install PyTorch (adjust for your CUDA version)
pip install torch torchvision torchaudio

# 4. Install main dependencies
pip install -r requirements.txt

# 5. Install DiffVG manually
git clone https://github.com/BachiLi/diffvg.git
cd diffvg
git submodule update --init --recursive
python setup.py install
cd ..

# 6. Install pysvgenius in development mode
pip install -e .
```

## 📦 Dependencies

### Core Dependencies
- `torch` - PyTorch for neural networks and optimization
- `torchvision` - Computer vision utilities
- `transformers` - Hugging Face transformers for SIGLIP
- `diffusers` - Diffusion models for image generation
- `pillow` - Image processing
- `numpy` - Numerical computing

### SVG Processing
- `diffvg` - Differential vector graphics (auto-installed)
- `cairosvg` - SVG to image conversion
- `svgpathtools` - SVG path manipulation
- `vtracer` - Raster to vector conversion

### Machine Learning Models
- `clip` - CLIP model for aesthetic evaluation
- `accelerate` - Hugging Face acceleration utilities
- `safetensors` - Safe tensor serialization

### Optional Dependencies
- `opencv-python` - Advanced image processing
- `scipy` - Scientific computing
- `matplotlib` - Plotting and visualization
- `jupyter` - Notebook support

## 🎯 Quick Start

### Basic Usage

```python
from pysvgenius import SVGOptimizer
from PIL import Image

# Initialize optimizer
optimizer = SVGOptimizer()

# Load target image
target_image = Image.open("target.jpg")

# Read SVG content
with open("input.svg", "r") as f:
    svg_content = f.read()

# Optimize SVG
optimized_svg, score = optimizer.optimize(
    svg_content=svg_content,
    target_image=target_image,
    iterations=200
)

# Save result
with open("optimized.svg", "w") as f:
    f.write(optimized_svg)
```

### Configuration

Create a `config.yaml` file:

```yaml
optimizer:
  diffvg:
    args:
      iterations: 200
      w_aesthetic: 100.0
      w_siglip: 100.0
      w_mse: 1000.0
      lr_points: 0.1
      lr_color: 0.01
      device: "cuda"
      
generator:
  sdxl-turbo:
    model_path: "stabilityai/sdxl-turbo"
    num_images: 5
    device: cuda
```

## 🔍 Troubleshooting

### Common Issues

#### DiffVG Installation Fails
```bash
# Make sure you have build tools
sudo apt install build-essential cmake

# Clear build cache and retry
rm -rf diffvg/build
cd diffvg && python setup.py install
```

#### CUDA Out of Memory
```python
# Reduce batch size in config
batch_size: 1

# Use CPU fallback
device: "cpu"
```

#### Model Download Issues
```bash
# Set Hugging Face cache directory
export HF_HOME=/path/to/cache
export TRANSFORMERS_CACHE=/path/to/cache
```

### Environment Variables

```bash
# Optional: Set cache directories
export HF_HOME="./models"
export TRANSFORMERS_CACHE="./models"
export TORCH_HOME="./models"

# CUDA settings
export CUDA_VISIBLE_DEVICES=0
```

## 📁 Project Structure

```
pysvgenius/
├── src/
│   ├── optimizer/          # SVG optimization algorithms
│   ├── generator/          # Image generation models
│   ├── ranker/            # Aesthetic and similarity models
│   ├── converter/         # Raster-to-vector conversion
│   └── utils/             # Utilities and helpers
├── configs/               # Configuration files
├── models/               # Pre-trained model cache
├── data/                 # Test data and results
└── notebooks/            # Example notebooks
```

## 🎨 Examples

See the `notebooks/` directory for detailed examples:
- `optimize_svg.ipynb` - Basic SVG optimization
- `sdxl_turbo.ipynb` - Image generation pipeline
- `test_paligemma_ranker.ipynb` - Aesthetic ranking
- `vtracer.ipynb` - Vector conversion

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [DiffVG](https://github.com/BachiLi/diffvg) - Differential vector graphics
- [CLIP](https://github.com/openai/CLIP) - Contrastive language-image pretraining
- [Hugging Face](https://huggingface.co/) - Transformers and model hub
- [VTracer](https://github.com/visioncortex/vtracer) - Raster to vector conversion

## 📞 Support

- Create an issue for bug reports
- Check existing issues for common problems
- Join discussions for feature requests