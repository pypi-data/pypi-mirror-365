from setuptools import setup, find_packages

setup(
    name="fakexyz",
    version="2.1",
    packages=find_packages(),
    include_package_data=True,
    package_data={"fakexyz": ["data/*.json"]},
    description="Generate fake user and address information for various countries.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Mahir Labib",
    author_email="islamraisul796@gmail.com",
    url="https://github.com/bbinl/fakexyz.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.7",
)
