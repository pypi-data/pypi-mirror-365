from setuptools import setup

setup(
    name="hertydlc",
    version="1.2",
    description="Упрощённый Python",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="ZlokLike",
    py_modules=["hertydlc"],
    install_requires=["colorama>=0.4.0"],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/ZlokLike",
)