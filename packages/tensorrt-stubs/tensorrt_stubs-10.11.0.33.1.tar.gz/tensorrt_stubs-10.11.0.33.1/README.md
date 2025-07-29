# tensorrt-stubs

Type stubs for NVIDIA TensorRT Python API.

## Description

This package provides type stubs for the NVIDIA TensorRT Python API. It enables static type checking and IDE autocompletion for TensorRT in Python projects.

## Installation

```bash
pip install tensorrt-stubs
```

## Usage

After installation, your IDE and type checkers (like mypy, pyright, etc.) will automatically use these stubs when you import TensorRT:

```python
import tensorrt as trt

# Your IDE will now provide autocompletion and type checking for TensorRT
builder = trt.Builder(trt.Logger(trt.Logger.INFO))
```

## Requirements

- Python >= 3.10
- TensorRT == 10.11.0.33

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.