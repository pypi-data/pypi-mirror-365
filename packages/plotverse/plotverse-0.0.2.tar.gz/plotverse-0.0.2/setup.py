from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="plotverse",
    version="0.0.2",
    author="Sanju",
    author_email="sanjayskpy1@gmail.com",
    description="Powerful data visualization and analysis library combining Pandas, Matplotlib, and Seaborn.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sk-sanju/plotverse",
    project_urls={
        "Source": "https://github.com/sk-sanju/plotverse",
        "Tracker": "https://github.com/sk-sanju/plotverse/issues",
    },
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pandas>=1.0.0",
        "matplotlib>=3.0.0",
        "seaborn>=0.11.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    python_requires='>=3.11',
    keywords="pandas matplotlib seaborn data visualization analysis",
)
