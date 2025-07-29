from setuptools import setup, find_packages

setup(
    name="pyadverse",
    version="0.0.1",
    packages=find_packages(),
    description="Risk Metrics library for financial analysis",
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
