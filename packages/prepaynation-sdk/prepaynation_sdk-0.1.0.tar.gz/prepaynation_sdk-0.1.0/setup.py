from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="prepaynation_sdk",
    version="0.1.0",
    description="Python SDK for Prepay Nation Top‑Up API v2",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ninjaroot-509",
    url="https://github.com/ninjaroot-509/prepaynation_sdk",
    packages=find_packages(),
    install_requires=[
        "requests>=2.20.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
