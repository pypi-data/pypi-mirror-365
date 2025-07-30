from setuptools import setup, find_packages

setup(
    name="topsis_Akshat_102203644",
    packages=find_packages(),
    version="1.2.5",
    author="Akshat Khurana",
    author_email="akhurana_be22@thapar.edu",
    description="A Python package to perform TOPSIS (Technique for Order Preference by Similarity to Ideal Solution).",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Akshatkhurana/TOPSIS-package",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "numpy",
        "pandas",
    ],
    entry_points={
        "console_scripts": [
            "topsis=topsis_Akshat_102203644.topsis:topsis",  # Replace `main` with your function handling CLI commands
        ],
    },
)
