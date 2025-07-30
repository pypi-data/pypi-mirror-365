from setuptools import setup, find_packages

setup(
    name="venv_stack",
    version="1.0",
    packages=find_packages(),
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "venv-stack=venv_stack.__main__:main",
        ]
    },
)