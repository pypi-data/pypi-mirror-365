

#### d. `setup.py`
import setuptools

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Get the version from your package's __init__.py
# You can also set it directly here
about = {}
with open("py_eio_logic/__init__.py", "r") as f:
    exec(f.read(), about)

setuptools.setup(
    name="py-eval_in_order", # This is the name that will be used on PyPI
    version=about["__version__"],
    author="Mostafa Hani", # Replace with your name
    author_email="mostafahanii213@gmail.com", # Replace with your email
    description="A Python package for evaluating multiple boolean conditions (uses eval) IN ORDER.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MostafaHanii/py_eio", # Replace with your GitHub repo URL
    packages=setuptools.find_packages(), # Automatically finds your package directory
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha", 
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='>=3.6', # Minimum Python version required
    keywords="boolean eval conditions logic", # Keywords for PyPI search
    
)