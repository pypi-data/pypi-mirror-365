from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="glazzbocks",
    version="0.1.0",
    description="An explainable, modular machine learning toolbox — a glass-box alternative to AutoML.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your@email.com",
    url="https://github.com/yourusername/glazzbocks",
    packages=find_packages(),
    install_requires=[
        "scikit-learn",
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "shap",
        "statsmodels"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
