# setup.py
from setuptools import setup, find_packages

setup(
    name="linkai-aion",
    version="0.1.5",
    author="Aksel",
    description="🚀 Smarter AI Utilities, Simplified - A comprehensive Python utility library by LinkAI for AI projects, automation, and productivity workflows.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.7",
    license="MIT",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)