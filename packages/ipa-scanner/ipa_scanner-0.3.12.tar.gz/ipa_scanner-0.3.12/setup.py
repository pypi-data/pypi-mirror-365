
from setuptools import setup, find_packages

setup(
    name="ipa-scanner",
    version="0.3.12",
    packages=find_packages(),
    install_requires=[
        "selenium>=4.0.0",
        "setuptools>=60.0.0",
        "pandas>=2.0.0"
    ],
    entry_points={
        "console_scripts": [
            "ipa-scan=ipa_scanner.main:main",
        ]
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="Automation tool for scanning SAP IPA BOM data using Selenium",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/skj370/ipa-scanner",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
