#!/usr/bin/env python3

from setuptools import setup
from pathlib import Path

import tomli

setup_dir = Path(__file__).parent

with open(setup_dir / "pyproject.toml", "rb") as fp:
    data = tomli.load(fp)

install_requires = []
extras_require = {}
all_requires = {}

tool_packages = data["tool"]["meta"]["packages"]

for ename, pkglist in data["tool"]["meta"]["extras"].items():
    extra = {}
    for pkg in pkglist:
        package = tool_packages[pkg]
        available = package.get("available", True)
        if not available:
            extra[ename] = f"{pkg}==0.0.0"
            continue

        version = package.get("version", None)
        min_version = package.get("min_version", None)
        max_version = package.get("max_version", None)
        constraint = package.get("constraint", None)

        if version in tool_packages:
            package = tool_packages[version]
            version = package.get("version", version)
            min_version = package.get("min_version", min_version)
            max_version = package.get("max_version", max_version)
            constraint = package.get("constraint", constraint)

        if version is not None:
            req = f"{pkg}{version}"
        elif min_version and max_version:
            req = f"{pkg}<{max_version},>={min_version}"
        else:
            raise ValueError(f"{pkg}: need version or min/max version")

        if constraint:
            req = f"{req}; {constraint}"

        extra[pkg] = req
        all_requires[pkg] = req

    if extra:
        if ename == "default":
            install_requires = list(extra.values())
        else:
            extras_require[ename] = list(extra.values())

if all_requires:
    extras_require["all"] = list(all_requires.values())

long_description = (setup_dir / "README.md").read_text()

setup(
    name="robotpy",
    description="Meta package to make installing robotpy easier",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="RobotPy Development Team",
    author_email="robotpy@googlegroups.com",
    url="https://github.com/robotpy/robotpy-meta",
    license="BSD-3-Clause",
    install_requires=install_requires,
    extras_require=extras_require,
    python_requires=">=3.9,<3.14",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development",
        "Topic :: Software Development :: Testing",
    ],
    use_scm_version=True,
)
