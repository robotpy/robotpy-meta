#!/usr/bin/env python3

import argparse
import subprocess
import sys
import typing

from packaging.version import Version


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("package")
    parser.add_argument("package_version")
    parser.add_argument("repo_version")
    args = parser.parse_args()

    package_version = Version(args.package_version)
    repo_version = Version(args.repo_version)

    if args.package == "mostrobotpy" and (
        repo_version.major != package_version.major
        or repo_version.minor != package_version.minor
        or repo_version.micro != package_version.micro
        or repo_version.pre != package_version.pre
    ):
        new_version = package_version
    else:
        # Only bump the super micro version unless its a beta
        if repo_version.pre:
            v = ".".join(map(str, repo_version.release))
            v = f"{v}{''.join(map(str, repo_version.pre))}"
            if repo_version.post:
                v = f"{v}.post{repo_version.post+1}"
            else:
                v = f"{v}.post1"
            new_version = Version(v)
        else:
            parts: list = list(repo_version.release)
            if len(parts) == 3:
                parts.append(1)
            else:
                parts[3] = int(parts[3]) + 1
            new_version = Version(".".join(map(str, parts)))

    assert new_version > repo_version
    print(new_version)
    return 0


if __name__ == "__main__":
    sys.exit(main())
