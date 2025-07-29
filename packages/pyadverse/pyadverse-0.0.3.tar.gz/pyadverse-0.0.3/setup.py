from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyadverse",
    version="0.0.3",
    packages=find_packages(),
    description="Risk Metrics library for financial analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",  # <-- This is crucial
    author="Ajeet Rai",
    license="MIT",
    include_package_data=True,
    install_requires=[
        "numpy",
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
