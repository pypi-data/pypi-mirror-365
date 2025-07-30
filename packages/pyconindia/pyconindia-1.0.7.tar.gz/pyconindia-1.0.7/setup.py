import setuptools
import os
import re

__project_name__ = "pyconindia"

with open("README.md", "r") as fh:
    long_description = fh.read()


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


setuptools.setup(
    name=__project_name__,
    version=get_version(__project_name__),
    author="PyCon India Team",
    author_email="contact@in.pycon.org",
    description="The largest gathering of Pythonistas in India for the Python programming language.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/anistark/pyconindia",
    packages=["pyconindia"],
    install_requires=[],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    python_requires='>=3.6',
)
