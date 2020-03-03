# -*- coding: utf-8; mode: python -*-
from pathlib import Path
from setuptools import find_packages, setup
from macropy import __version__

here = Path(__file__).absolute().parent
with (here / 'CHANGES.rst').open(encoding='utf-8') as f:
    CHANGES = f.read()
with (here / 'readme.rst').open(encoding='utf-8') as f:
    README = f.read()

setup(
    name='macropy3',
    version=__version__,
    description='Macros for Python: Quasiquotes, Case Classes, LINQ and more!',
    long_description=README + '\n\n' + CHANGES,
    license='MIT',
    author='Li Haoyi, Justin Holmgren',
    author_email='haoyi.sg@gmail.com, justin.holmgren@gmail.com',
    maintainer='Alberto Berti',
    maintainer_email='alberto@metapensiero.it',
    url='https://github.com/lihaoyi/macropy',
    packages=find_packages(exclude=["*.test", "*.test.*"]),
    extras_require={
        'pyxl':  ["pyxl3"],
        'pinq': ["SQLAlchemy"],
        'js_snippets': ["selenium", "pjs"],
    },
    install_requires=[],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Code Generators',
    ],
    python_requires='>=3.4,<3.8',
    project_urls={
        'Documentation': 'http://macropy3.readthedocs.io/en/latest/index.html',
    }
)
