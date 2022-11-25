#!/usr/bin/env python3

import sys

if sys.version_info < (3, 7):
    sys.stderr.write("ERROR: RobotPy requires Python 3.7+\n")
    exit(1)

import subprocess
from setuptools import find_packages, setup
from pathlib import Path

setup_dir = Path(__file__).parent
git_dir = setup_dir / ".git"
base_package = "robotpy"
version_file = setup_dir / base_package / "version.py"

# Automatically generate a version.py based on the git version
if git_dir.exists():
    p = subprocess.Popen(
        ["git", "describe", "--tags", "--long", "--dirty=-dirty"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = p.communicate()
    # Make sure the git version has at least one tag
    if err:
        print("Error: You need to create a tag for this repo to use the builder")
        sys.exit(1)

    # Convert git version to PEP440 compliant version
    # - Older versions of pip choke on local identifiers, so we can't include the git commit
    v, commits, local = out.decode("utf-8").rstrip().split("-", 2)
    if commits != "0" or "-dirty" in local:
        v = "%s.post0.dev%s" % (v, commits)

    # Create the version.py file
    with open(version_file, "w") as fp:
        fp.write("# Autogenerated by setup.py\n__version__ = '{0}'".format(v))

if version_file.exists():
    with open(version_file, "r") as fp:
        exec(fp.read(), globals())
else:
    __version__ = "master"


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

    extras_require[key] = reqs
    all_reqs |= set(reqs)

extras_require["all"] = all_reqs

long_description = (setup_dir / "README.md").read_text()

setup(
    name="robotpy",
    version=__version__,
    description="Meta package to make installing robotpy easier",
    long_description=long_description,
    author="RobotPy Development Team",
    author_email="robotpy@googlegroups.com",
    url="https://github.com/robotpy/robotpy-meta",
    license="BSD-3-Clause",
    packages=find_packages(),
    install_requires=install_requires,
    extras_require=extras_require,
    python_requires=">=3.7,<3.12",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development",
        "Topic :: Software Development :: Testing",
    ],
)
