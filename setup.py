from setuptools import setup
import pathlib
import re

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

version = ''
with open('rud/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

setup(
    name="rud",
    version=version,
    description="python cli and async library to selectively download a reddit user's posts",
    long_description=README,
    long_description_content_type="text/markdown",
    author="anytarseir67",
    url="https://github.com/anytarseir67/rud",
    license="GPLv3",
    packages=["rud"],
    install_requires=requirements,
    entry_points={
        "console_scripts": ["rud=rud.cli:main"],
    },
    extras_require={
        'docs': [
            'sphinx',
            'sphinxcontrib_trio',
            'sphinxcontrib-websupport',
            'typing-extensions',
            'myst_parser',
            'sphinx-argparse'
        ],
    },
)
