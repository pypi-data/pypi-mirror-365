# Plotverse
strategy:
  matrix:
    python-version: [3.11, 3.12, 3.13]
    
**Plotverse** is a unified Python library that combines:

- All functionality from `pandas`
- All `matplotlib.pyplot` functions (prefixed as `plt_`)
- All `seaborn` functions (prefixed as `sns_`)

## 📦 Installation

```bash
pip install .

## 🧠 Usage

import plotverse as pv

df = pv.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
pv.plt_plot(df['x'], df['y'])
pv.sns_heatmap(df.corr())

## 🎨 Themes

from plotverse.theme import dark_mode, light_mode

dark_mode()
# or
light_mode()

---

### 📦 `setup.py`
```python
from setuptools import setup, find_packages

setup(
    name="plotverse",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "matplotlib",
        "seaborn"
    ],
    author="Sanju",
    description="A combined wrapper for Pandas, Matplotlib, and Seaborn.",
    url="https://github.com/sk-sanju/plotverse",
    license="MIT",
)

📄 LICENSE (MIT)

MIT License

Copyright (c) 2025 sk-sanju

💡 Folder Structure

plotverse/
├── plotverse/
│   ├── __init__.py
│   └── theme/
│       └── __init__.py
├── tests/
│   └── test_imports.py
├── README.md
├── setup.py
└── LICENSE

