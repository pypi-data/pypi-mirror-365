from setuptools import setup, find_packages

setup(
    name="SFDL_DB",
    version="0.1.0",
    description="Same Features, Different Label Skew Generator",
    author="Your Name",
    author_email="your.email@example.com",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "matplotlib",
        "scikit-learn"
    ],
    include_package_data=True,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/SFDL_DB",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
)
