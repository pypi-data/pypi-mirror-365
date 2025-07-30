# KDTreeFiltering

KDTreeFiltering is a Python library for efficient spatial and bilateral filtering using Gaussian KDTree data structures. It provides fast and scalable filtering operations for multidimensional data, leveraging the power of KD-trees for neighborhood queries and Gaussian kernels for smoothing.

## Features
- Spatial filtering using KDTree and Gaussian kernels
- Bilateral filtering for edge-preserving smoothing
- Efficient for high-dimensional data

## Installation
```bash
pip install guaskd
```

## Usage
```python
from guaskd.kdtree import Filtering

# Example usage
filtered = Filtering(data, mode = 'Bilateral')
```