from setuptools import setup, find_packages

setup(
    name="tolisp",
    version="0.1.0",
    packages=find_packages(),
    author="Ankit Kumar Ravi",
    description="Convert YAML/JSON files to Lisp style S-expressions",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/riAssinstAr",
    license="MIT",
    python_requires=">=3.7",
    install_requires=["pyyaml"],
    entry_points={
        "console_scripts": [
            "tolisp=tolisp.main:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ]
)
