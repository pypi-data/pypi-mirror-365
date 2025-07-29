# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="jaganathanj",
    version="1.0.0",
    author="Jaganathan J",
    author_email="jaganathanjjds@gmail.com",
    description="A unique personal brand package - because why have a boring resume when you can pip install a person details?",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/J-Jaganathan/jaganathanj-package",
    project_urls={
        "Portfolio": "https://jaganathan-j-portfolio.vercel.app/",
        "LinkedIn": "https://linkedin.com/in/jaganathan-j-a5466a257",
        "YouTube": "https://youtube.com/@Tech_CrafterX",
        "Bug Tracker": "https://github.com/J-Jaganathan/jaganathanj-package/issues",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Documentation",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        # No external dependencies - keeping it lightweight!
    ],
    keywords="resume portfolio personal-brand cv developer student",
    entry_points={
        "console_scripts": [
            "jaganathanj=jaganathanj:_welcome_message",
        ],
    },
)