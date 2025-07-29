from setuptools import setup, find_packages

setup(
    name="hello-from-shiphero",
    version="0.0.1",
    description="PoC for dependency confusion by Ousski",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Ousski",
    author_email="ousskr@gmail.com",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)
