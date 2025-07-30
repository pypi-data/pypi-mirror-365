from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="plotverse",
    version="0.0.9",
    description="Powerful data visualization and analysis library combining Pandas, Matplotlib, and Seaborn.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Sanju",
    author_email="sanjayskpy1@gmail.com",
    url="https://github.com/sk-sanju/plotverse",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "pandas==2.2.2",
        "matplotlib==3.8.4",
        "seaborn==0.13.2"
    ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
