from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_desc = f.read()

setup(
    name="getnet_sdk",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    author="ninjaroot-509",
    url="https://github.com/ninjaroot-509/getnet_sdk",
    project_urls={
        "Source": "https://github.com/ninjaroot-509/getnet_sdk",
    },
    description="Python SDK for integrating with the Getnet payment API",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
