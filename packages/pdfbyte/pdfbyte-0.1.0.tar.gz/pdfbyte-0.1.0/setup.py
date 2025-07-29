from setuptools import setup, find_packages

setup(
    name="pdfbyte",  # Name of your package
    version="0.1.0",  # Initial version
    install_requires=[
        # "requests",
    ],
    author="Ramesh Chandra",
    author_email="rameshsofter@gmail.com",
    description="A simple package for working with PDFs",
    long_description=open('README.md').read(),  # Optional: include a README
    long_description_content_type="text/markdown",
    packages=find_packages(),  # This will find all the packages in your project
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
