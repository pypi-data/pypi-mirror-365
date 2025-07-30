#!/usr/bin/env python3

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="nba-summer-league-headshots",
    version="1.0.0",
    author="Thavas Antonio",  # Replace with your name
    author_email="thavasantonio@gmail.com",  # Replace with your email
    description="NBA Summer League 2025 Player Headshots API - Access 431+ verified player images",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BuddyBob/summer_league_headshot_api",  # Replace with your repo URL
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Sports",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Add any dependencies here if needed
    ],
    include_package_data=True,
    package_data={
        "nba_summer_league_headshots": [
            "NBA_Roster_Clean.csv",
            "NBA_Combined_Headshots/*.jpg",
            "NBA_Combined_Headshots/*.png",
        ],
    },
    entry_points={
        "console_scripts": [
            "nba-headshots=nba_summer_league_headshots.cli:main",
        ],
    },
    keywords="nba, basketball, headshots, summer league, sports, api",
    project_urls={
        "Bug Reports": "https://github.com/BuddyBob/summer_league_headshot_api/issues",
        "Source": "https://github.com/BuddyBob/summer_league_headshot_api",
    },
)
