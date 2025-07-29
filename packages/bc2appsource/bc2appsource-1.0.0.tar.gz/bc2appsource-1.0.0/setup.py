from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Define requirements directly to avoid file reading issues in isolated build environments
requirements = [
    "requests>=2.31.0",
    "click>=8.0.0",
]

setup(
    name="bc2appsource",
    version="1.0.0",
    author="Attie Retief",
    author_email="attie@example.com",
    description="A tool to publish Business Central apps to Microsoft AppSource",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/attieretief/bc2appsource",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Build Tools",
        "Topic :: System :: Software Distribution",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "bc2appsource=bc2appsource.cli:main",
        ],
    },
    keywords="business-central appsource microsoft dynamics365",
    project_urls={
        "Bug Reports": "https://github.com/attieretief/bc2appsource/issues",
        "Source": "https://github.com/attieretief/bc2appsource",
        "Documentation": "https://github.com/attieretief/bc2appsource#readme",
    },
)
