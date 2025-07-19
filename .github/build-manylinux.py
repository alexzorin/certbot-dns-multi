#!/usr/bin/env python3

import argparse
import os
import pathlib
import subprocess
from sys import stdout, stderr
from typing import List

MANYLINUX_IMAGES = {"arm64": "manylinux_2_28_aarch64", "amd64": "manylinux_2_28_x86_64"}


def _run_process(args: List[str]) -> None:
    print(f"Running: {' '.join(args)}")
    proc = subprocess.Popen(args, stdout=stdout, stderr=stderr)
    return_code = proc.wait(1800)
    if return_code != 0:
        raise RuntimeError(f"Process failed, exit code {return_code}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arch", required=True, type=str)
    parser.add_argument(
        "--go-version",
        default="1.24.5",
        type=str,
        help="Go compiler version (default: %(default)s)",
    )
    parser.add_argument(
        "--python-versions",
        default=["cp39-cp39", "cp310-cp310", "cp311-cp311", "cp312-cp312"],
        type=str,
        nargs="+",
        help="Which Python versions to generate wheels from (default %(default)s)",
    )
    args = parser.parse_args()

    project_dir = pathlib.Path(__file__).parent.parent
    wheels_dir = project_dir.joinpath("dist")
    os.makedirs(wheels_dir, exist_ok=True)

    image = MANYLINUX_IMAGES.get(args.arch, None)
    if not image:
        raise RuntimeError(f"Architecture {args.arch} is not supported")

    print(f"Building wheels via {image}")
    _run_process(
        [
            "docker",
            "run",
            "--platform",
            f"linux/{args.arch}",
            "--rm",
            "-e",
            f"PY_VERS={' '.join(args.python_versions)}",
            "-e",
            f"GO_VER={args.go_version}",
            "-e",
            f"GOARCH={args.arch}",
            "-e",
            f"PY_PLAT={image}",
            "-v",
            f"{str(wheels_dir.absolute())}:/wheels",
            "-v",
            f"{str(project_dir.absolute())}:/app",
            f"quay.io/pypa/{image}",
            "/app/.github/build-wheel.sh",
        ]
    )


if __name__ == "__main__":
    main()
