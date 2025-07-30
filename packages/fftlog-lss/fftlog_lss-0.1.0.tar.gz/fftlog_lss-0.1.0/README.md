# FFTLog

A Python implementation of FFTLog for fast logarithmic FFT transforms, developed for [PyBird](https://github.com/pierrexyz/pybird).

## Installation

### From PyPI (recommended)
```bash
pip install fftlog-lss
```

### From source
```bash
git clone https://github.com/pierrexyz/fftlog.git
cd fftlog
pip install --editable .
```

## Dependencies

- Python >= 3.8
- numpy >= 1.20.0
- scipy >= 1.7.0

## Usage

FFTLog provides fast logarithmic FFT transforms for scientific computing applications. Here's a basic example:

```python
import numpy as np
from fftlog import FFTLog

# Initialize FFTLog
fftlog = FFTLog(
    Nmax=1024,      # Number of points
    xmin=1e-3,      # Minimum x value
    xmax=1e3,       # Maximum x value
    bias=0.0,       # Bias parameter
    complex=False   # Use real FFT
)

# Example function
x = np.logspace(-3, 3, 1000)
f = np.exp(-x**2)  # Gaussian function

# Transform
result = fftlog.rec(x, f)
```

## Features

- Fast logarithmic FFT transforms
- Support for both real and complex transforms
- Spherical Bessel transforms
- Anti-aliasing windows
- Optimized for Large Scale Structure cosmology

## Documentation

For more detailed examples and documentation, see the notebooks in the `notebooks/` directory.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.



