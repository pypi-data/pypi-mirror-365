from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union

import orjson
from loguru import logger
from sbt.misc import cache_method, exec
from sbt.package.package import Package

PBT_CONFIG_FILE_NAME = "pbtconfig.json"
PBT_LOCK_FILE_NAME = "pbt.lock"
PBT_IGNORE_FILE_NAME = ".pbtignore"


@dataclass
class PBTConfig:
    # current working directory
    cwd: Path
    # directory
    cache_dir: Path = Path("./.cache")
    # set of packages that we ignore
    ignore_packages: set[str] = field(default_factory=set)
    # set of directories (absolute path) that we ignore and not search for packages in them
    ignore_directories: set[Path] = field(default_factory=set)
    # set of directory name that we ignore and not search for packages in them
    ignore_directory_names: set[str] = field(default_factory=set)
    # packages that do not contain any code with sole purpose for installing dependencies or creating working environment
    phantom_packages: set[str] = field(default_factory=set)
    # use pre-built binaries for the package if available (i.e., rely on the package registry to find an installable version)
    use_prebuilt_binaries: set[str] = field(default_factory=set)
    # freeze the following packages and don't update their dependencies
    freeze_packages: set[str] = field(default_factory=set)
    # directory to store the built artifacts for release (relative to each package's location)
    distribution_dir: Path = Path("./dist")
    # the virtualenv directory (default is .venv in the project root directory)
    python_virtualenv_path: str = "./.venv"
    # python executable to use for building and installing packages, default (None) is the sys.executable
    python_path: Optional[Path] = None
    # path to the directory containing dependencies
    library_path: Path = Path("./libraries")
    # list of repositories of dependencies
    dependency_repos: list[str] = field(default_factory=list)

    @staticmethod
    def from_dir(cwd: Union[Path, str], force: bool = False) -> "PBTConfig":
        if not force:
            # get git top module
            try:
                output = exec(
                    "git rev-parse --show-superproject-working-tree --show-toplevel",
                    cwd="." if cwd == "" else cwd,
                )
                if len(output) == 1:
                    cwd = output[0]
                else:
                    for i in range(len(output)):
                        if all(
                            output[j].startswith(output[i])
                            for j in range(i + 1, len(output))
                        ):
                            cwd = output[i]
                            break
                    else:
                        raise Exception(
                            "Unreachable error. Can't figure out which folder contains your project. Congrat! You found a bug.\nAvailable options:\n"
                            + "\n\t".join(output)
                        )
            except Exception as e:
                if not str(e).startswith("fatal: not a git repository"):
                    # another error not related to git
                    raise
                else:
                    cwd = cwd

        cwd = Path(cwd).absolute()
        cache_dir = cwd / ".cache"
        cache_dir.mkdir(exist_ok=True, parents=True)

        if (cwd / PBT_CONFIG_FILE_NAME).exists():
            with open(cwd / PBT_CONFIG_FILE_NAME, "r") as f:
                cfg = orjson.loads(f.read())
        else:
            cfg = {}

        if (cwd / PBT_IGNORE_FILE_NAME).exists():
            with open(cwd / PBT_IGNORE_FILE_NAME, "r") as f:
                instructions = {x.strip() for x in f.readlines()}
                if "" in instructions:
                    instructions.remove("")
                ignore_directories = set()
                ignore_directory_names = set()
                for instruction in instructions:
                    if instruction.startswith("/"):
                        ignore_directories.add((cwd / instruction[1:]).resolve())
                    else:
                        assert "/" not in instruction, instruction
                        ignore_directory_names.add(instruction)
        else:
            ignore_directories = set()
            ignore_directory_names = set()

        logger.info("Root directory: {}", cwd)

        if "python_path" not in cfg:
            # try use python_path from the environment variable: `PBT_PYTHON`
            python_path = os.environ.get("PBT_PYTHON", None)
        else:
            python_path = cfg["python_path"]

        python_virtualenv_path = cfg.get(
            (
                "python_virtualenv_path"
                if "python_virtualenvs_path" not in cfg
                else "python_virtualenvs_path"
            ),
            os.environ.get("PYTHON_VIRTUALENV_PATH", "./.venv"),
        )
        logger.info(
            "Virtual environment directory (should be relative path): {}",
            python_virtualenv_path,
        )

        return PBTConfig(
            cwd=cwd,
            cache_dir=cache_dir,
            ignore_packages=set(cfg.get("ignore_packages", [])),
            ignore_directories=ignore_directories.union(
                cfg.get("ignore_directories", [])
            ),
            ignore_directory_names=ignore_directory_names.union(
                cfg.get("ignore_directory_names", [])
            ),
            phantom_packages=set(cfg.get("phantom_packages", [])),
            use_prebuilt_binaries=set(cfg.get("use_prebuilt_binaries", [])),
            freeze_packages=set(cfg.get("freeze_packages", [])),
            distribution_dir=Path(cfg.get("distribution_dir", "./dist")),
            python_virtualenv_path=python_virtualenv_path,
            python_path=Path(python_path) if python_path is not None else None,
            library_path=Path(cfg.get("library_path", "./libraries")),
            dependency_repos=cfg.get("dependency_repos", []),
        )

    def pkg_cache_dir(self, pkg: Package) -> Path:
        """Get the cache directory for a package that we can use for storing temporary files
        during building and installing packages
        """
        pkg_dir = self.cache_dir / pkg.name
        pkg_dir.mkdir(exist_ok=True, parents=True)
        return pkg_dir

    @cache_method()
    def get_python_path(self) -> str:
        if self.python_path is not None:
            if not self.python_path.exists():
                raise ValueError("Python does not exist: {}".format(self.python_path))
            return str(self.python_path)
        else:
            return sys.executable

    @cache_method()
    def get_python_version(self) -> str:
        version = "".join(exec([self.get_python_path(), "--version"])).strip()
        assert version.startswith("Python "), version
        return version[len("Python ") :].strip()
