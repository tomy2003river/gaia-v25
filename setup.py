from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gaia-core",
    version="25.0.0",
    author="GAIA Team",
    description="GAIA v25 - Multimodal AI Assistant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "pyttsx3>=2.90",
        "python-dotenv>=1.0.0",
        "spacy>=3.7.0",
        "wikipedia-api>=0.6.0",
        "numpy>=1.24.0",
    ],
)
