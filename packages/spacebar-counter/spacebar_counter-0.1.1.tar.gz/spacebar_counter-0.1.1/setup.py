from setuptools import setup, find_packages

setup(
    name="spacebar-counter",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "pynput",
        "plotly",
        "typer",
    ],
    entry_points={
        "console_scripts": [
            "spacebar-counter=spacebar_counter.cli:app",
        ],
    },
    author="Your Name",
    description="A CLI tool to count spacebar presses.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
)
