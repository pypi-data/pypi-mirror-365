from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="intronator",
    version="0.2.1",
    author="Intronator Team",
    author_email="contact@intronator.org",
    description="A Python package for comprehensive splice site analysis and simulation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/intronator/intronator",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="bioinformatics splicing genomics splice-sites RNA mutations",
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov",
            "black",
            "isort",
            "flake8",
            "build",
            "twine",
        ],
        "ml": [
            "torch>=1.10.0",
            "tensorflow>=2.8.0",
            "keras>=2.8.0",
            "absl-py",
        ],
        "external": [
            "spliceai",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/intronator/intronator/issues",
        "Source": "https://github.com/intronator/intronator",
        "Documentation": "https://intronator.readthedocs.io",
    },
)