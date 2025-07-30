import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="FeatureEng_arun8nov",  
    version="0.0.2",
    author="Arunprakash",
    author_email="arunbabuprakash@gmail.com", 
    description="A collection of feature engineering methods for preprocessing datasets.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arun8nov/FeatureEng", 
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'pandas',
        'numpy',
    ],
)