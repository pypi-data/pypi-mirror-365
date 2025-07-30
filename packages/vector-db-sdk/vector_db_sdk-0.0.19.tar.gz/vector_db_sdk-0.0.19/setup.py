import codecs
import os
import sys
from io import open

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


def read(filename):
    """Read and return `filename` in root dir of project and return string ."""
    here = os.path.abspath(os.path.dirname(__file__))
    return codecs.open(os.path.join(here, filename), "r").read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


version = get_version("vector_db_sdk/__init__.py")
print('version:%s' % version)

install_requires = None
if os.path.exists("requirements.txt"):
    install_requires = read("requirements.txt").split()

setup(
    name="vector-db-sdk",
    version=version,
    description="A unified Python SDK for vector databases supporting pgvector and tcvector",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="v_fchtan",
    author_email="v_fchtan@global.tencent.com",
    license="MIT",
    url="https://github.com/your-username/vector-db-sdk",  # 替换为你的实际仓库地址
    packages=find_packages(exclude=["test*", "scripts*"]),
    include_package_data=True,
    install_requires=install_requires,
    zip_safe=False,
    keywords="vector database, pgvector, tcvector, embedding, similarity search",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    extras_require={
        "dev": ["pytest", "pytest-cov", "black", "flake8", "mypy"],
        "docs": ["sphinx", "sphinx-rtd-theme"],
    },
    project_urls={
        "Bug Reports": "https://github.com/your-username/vector-db-sdk/issues",
        "Source": "https://github.com/your-username/vector-db-sdk",
        "Documentation": "https://github.com/your-username/vector-db-sdk#readme",
    },
)
