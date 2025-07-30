from setuptools import setup, find_packages
import os

# Read long description from README
def read_long_description():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="mkdocs-cc-license-plugin",
    version="1.0.1",
    author="Jérôme Bezet-Torres",
    author_email="bezettorres.jerome@gmail.com",
    description="MkDocs plugin for automatic Creative Commons license management",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/JM2K69/mkdocs-cc-license-plugin",
    project_urls={
        "Bug Reports": "https://github.com/JM2K69/mkdocs-cc-license-plugin/issues",
        "Source": "https://github.com/JM2K69/mkdocs-cc-license-plugin",
        "Documentation": "https://github.com/JM2K69/mkdocs-cc-license-plugin/blob/main/README.md",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Framework :: MkDocs",
    ],
    keywords="mkdocs plugin creative-commons license documentation",
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.900",
        ],
        "examples": [
            "mkdocs-static-i18n>=0.53",
            "mkdocs-material>=8.0",
        ],
    },
    entry_points={
        "mkdocs.plugins": [
            "cc-license = mkdocs_cc_license_plugin.plugin:CreativeCommonsPlugin",
        ]
    },
    include_package_data=True,
    zip_safe=False,
)
