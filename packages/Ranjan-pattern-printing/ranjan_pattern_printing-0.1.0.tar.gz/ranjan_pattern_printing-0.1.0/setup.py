from setuptools import setup, find_packages

setup(
    name="Ranjan_pattern_printing",
    version="0.1.0",
    author="Ranjan Sahoo",
    author_email="ranjansahoo905@gmail.com",
    description="This is used to print package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ranjansahoo905/Analyticswithranjan/tree/main/PYTHON",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)