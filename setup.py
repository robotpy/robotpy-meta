#!/usr/bin/env python3

from setuptools import find_packages, setup
from pathlib import Path

setup_dir = Path(__file__).parent


def get_reqs_from_path(path):
    return [
        req
        for req in Path(path).read_text().splitlines()
        if req and not req.startswith("#")
    ]


install_requires = get_reqs_from_path(setup_dir / "requirements.txt")
all_reqs = set(install_requires)

extras_require = {}

for fpath in setup_dir.glob("*-requirements.txt"):
    key = fpath.stem[:-13]  # stem doesn't have .txt

    reqs = get_reqs_from_path(fpath)
    if reqs:
        extras_require[key] = reqs
        all_reqs |= set(reqs)

extras_require["all"] = all_reqs

long_description = (setup_dir / "README.md").read_text()

setup(
    name="robotpy",
    description="Meta package to make installing robotpy easier",
    long_description=long_description,
    author="RobotPy Development Team",
    author_email="robotpy@googlegroups.com",
    url="https://github.com/robotpy/robotpy-meta",
    license="BSD-3-Clause",
    install_requires=install_requires,
    extras_require=extras_require,
    python_requires=">=3.8,<3.13",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development",
        "Topic :: Software Development :: Testing",
    ],
    use_scm_version=True,
)
