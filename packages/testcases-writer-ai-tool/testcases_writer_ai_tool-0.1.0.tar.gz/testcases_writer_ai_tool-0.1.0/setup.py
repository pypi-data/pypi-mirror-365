from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="testcases-writer-ai-tool",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Automatically generate pytest test cases for your Python app using Claude AI.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/testcases-writer-ai-tool",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pytest"
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "generate-test-cases = testcases_writer_ai_tool.generate_test_cases:main"
        ]
    },
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 