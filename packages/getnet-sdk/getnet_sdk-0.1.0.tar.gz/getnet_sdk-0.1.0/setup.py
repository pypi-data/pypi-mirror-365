from setuptools import setup, find_packages

setup(
    name="getnet_sdk",
    version="0.1.0",
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
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
