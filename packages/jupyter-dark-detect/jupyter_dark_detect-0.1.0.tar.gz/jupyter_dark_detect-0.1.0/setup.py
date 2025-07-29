"""Setup configuration for jupyter-dark-detect."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="jupyter-dark-detect",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Detect dark mode in Jupyter environments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/jupyter-dark-detect",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Jupyter",
        "Framework :: Jupyter :: JupyterLab",
        "Environment :: Web Environment",
    ],
    python_requires=">=3.7",
    install_requires=[
        "ipython>=7.0.0",
    ],
    keywords="jupyter notebook jupyterlab dark-mode theme detection",
    license="MIT",
    include_package_data=True,
)