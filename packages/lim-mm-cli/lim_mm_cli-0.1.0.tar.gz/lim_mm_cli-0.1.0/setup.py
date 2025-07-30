from setuptools import setup, find_packages

setup(
    name="lim-mm-cli",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "typer[all]",
        "jsonschema",
        "requests"
    ],
    entry_points={
        "console_scripts": [
            "mm=mm.cli:app",
        ]
    },
)
