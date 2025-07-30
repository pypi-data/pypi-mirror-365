from setuptools import setup, find_packages

setup(
    name="arthaLM",
    version="0.1.0",
    author="Vyom N. Patel",
    description="Plug-and-play pipeline for Artha LLM",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/vyomie/artha",  # Replace with your GitHub
    packages=find_packages(),
    install_requires=[
        "torch",
        "transformers",
        "tqdm",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
