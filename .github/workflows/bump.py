#!/usr/bin/env python3

import argparse
import pathlib
import sys

import tomlkit

root = pathlib.Path(__file__).parent.parent.parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("package")
    parser.add_argument("package_version")
    parser.add_argument("repo_version")
    args = parser.parse_args()

    # Package version year must match repo version year, otherwise we can end
    # up with users trying to install the prior year's packages and they
    # install a mess instead
    if args.repo_version.split(".")[0] != args.package_version.split(".")[0]:
        print("!! Package version year does not match repo version year!")
        return 1

    with open(root / "pyproject.toml") as fp:
        data = tomlkit.load(fp)

    pkg = data["tool"]["meta"]["packages"][args.package]
    if "version" in pkg:
        pkg["version"] = f"=={args.package_version}"
    elif "min_version" in pkg:
        pkg["min_version"] = args.package_version
    else:
        raise ValueError("unknown format")

    with open(root / "pyproject.toml", "w") as fp:
        tomlkit.dump(data, fp)

    return 0


if __name__ == "__main__":
    sys.exit(main())
