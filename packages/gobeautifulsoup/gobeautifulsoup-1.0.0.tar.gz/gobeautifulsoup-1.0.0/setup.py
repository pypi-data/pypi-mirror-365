"""
Setup script for GoBeautifulSoup Python package
"""

from setuptools import setup, find_packages
import os

# Read README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Include all shared libraries
def get_package_data():
    package_data = []
    libs_dir = os.path.join("gobeautifulsoup", "libs")
    
    if os.path.exists(libs_dir):
        for root, dirs, files in os.walk(libs_dir):
            for file in files:
                if file.startswith("libgobeautifulsoup"):
                    rel_path = os.path.relpath(
                        os.path.join(root, file), 
                        "gobeautifulsoup"
                    )
                    package_data.append(rel_path)
    
    return {"gobeautifulsoup": package_data}

setup(
    name="gobeautifulsoup",
    version="1.0.0",
    author="CoffeeCMS Team",
    author_email="team@coffeecms.com",
    description="A high-performance BeautifulSoup replacement powered by Go",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/coffeecms/gobeautifulsoup",
    packages=find_packages(),
    package_data=get_package_data(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Go",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: XML",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No Python dependencies - uses Go backend
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "beautifulsoup4>=4.10.0",
            "lxml>=4.6.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.991",
            "requests>=2.25.0",
        ],
        "test": [
            "pytest>=6.0",
            "beautifulsoup4>=4.10.0",
            "lxml>=4.6.0",
            "requests>=2.25.0",
        ],
        "benchmark": [
            "beautifulsoup4>=4.10.0",
            "lxml>=4.6.0",
            "memory-profiler>=0.60.0",
            "requests>=2.25.0",
        ]
    },
    keywords="html xml parsing beautifulsoup go performance web-scraping",
    project_urls={
        "Bug Reports": "https://github.com/coffeecms/gobeautifulsoup/issues",
        "Source": "https://github.com/coffeecms/gobeautifulsoup",
        "Documentation": "https://gobeautifulsoup.readthedocs.io/",
        "Changelog": "https://github.com/coffeecms/gobeautifulsoup/blob/main/CHANGELOG.md",
        "Benchmarks": "https://github.com/coffeecms/gobeautifulsoup/tree/main/benchmarks",
    },
    zip_safe=False,  # Because we include native libraries
)
