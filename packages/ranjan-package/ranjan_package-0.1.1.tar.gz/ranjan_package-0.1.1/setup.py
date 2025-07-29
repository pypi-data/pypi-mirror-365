from setuptools import setup, find_packages

setup(
    name="ranjan-package",
    version="0.1.1",
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