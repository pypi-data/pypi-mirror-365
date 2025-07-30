import re
from pathlib import Path
from setuptools import setup, find_packages  # type: ignore


def is_requirement(s: str) -> bool:
    """Returns true if the string is a valid requirement.
    For the requirement to be valid, it must be non empty
    and must not start from - or #.
    """
    s = s.strip()
    return not any([not s, re.match("^[-#]", s)])


requirements = [
    line.strip()
    for line in Path("requirements.txt").read_text().splitlines()
    if is_requirement(line)
]

setup(
    name="quantplay-lab",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    version="0.1.0",
    install_requires=requirements,
    tests_require=[],
    packages=find_packages(),
    url="https://github.com/yourusername/quantlab",
    package_data={"quantlab": ["py.typed"]},
    license="MIT",
    author="Your Name",
    author_email="your.email@example.com",
    description="High-performance backtesting engine for algorithmic trading with focus on Indian markets",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
)
