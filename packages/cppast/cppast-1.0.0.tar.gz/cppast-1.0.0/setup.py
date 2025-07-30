from setuptools import setup, find_packages # type: ignore

setup(
    name="cppast",
    version="1.0.0",
    description="C++ AST CLI tool with AST/graph visualization and pattern matching",
    author="Abhishek Manhas",
    license="MIT",
    packages=find_packages(include=["cppast", "core", "core.*"]),
    install_requires=[
        "clang",
        "graphviz",
        "networkx",
        "typer[all]"
    ],
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/amanhas/cppast",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        'console_scripts': [
            'cppast=core.__main__:main',
        ],
    },
    include_package_data=True,
)
