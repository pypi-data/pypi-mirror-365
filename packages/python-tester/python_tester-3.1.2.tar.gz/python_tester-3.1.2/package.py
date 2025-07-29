#! /usr/bin/env python3
import os
import shutil
from importlib.util import find_spec
from pathlib import Path

import src


def read_requirements(filename):
    with open(filename) as f:
        return f.readlines()


def find_modules_files(dir, ext):
    """
    dir: str, ext: list
    ext = file extensions to find
    Rewrite with yield of https://stackoverflow.com/a/59803793
    """
    for f in os.scandir(dir):
        if f.is_dir():
            yield from find_modules_files(f.path, ext)
        if f.is_file():
            if os.path.splitext(f.name)[1].lower() in ext:
                yield f.path


def create_build_file_path(file_path, module, dir_):
    path_as_list = file_path.split("/")
    module_dir_index = path_as_list.index(module)
    build_file_path = f"{dir_}/examiner/" + "/".join(path_as_list[module_dir_index:])
    return build_file_path


def find_modules_paths(modules):
    for module in modules:
        module_path = find_spec(module).origin
        module_path = os.path.dirname(module_path)
        yield (module, module_path)


def copy_and_insert_pylint_disable(modules, dir_):
    """
    Insert "# pylint: skip-file" in all module files because of bug in pylint.
    Bug make it so we cant ignore directories.
    https://github.com/PyCQA/pylint/issues/2686
    """
    inject_lines = "# pylint: skip-file\n"

    for module, module_path in find_modules_paths(modules):
        for file_ in find_modules_files(module_path, [".py"]):
            with open(file_, "r") as copy:
                content = copy.read()
                content = inject_lines + content

                build_path = create_build_file_path(file_, module, dir_)
                Path(os.path.dirname(build_path)).mkdir(parents=True, exist_ok=True)
                with open(build_path, "w") as paste:
                    paste.write(content)


def build(dir_, make_archive=False):
    module_name = "examiner"
    try:
        shutil.rmtree(f"{dir_}/{module_name}")
    except FileNotFoundError:
        pass
    try:
        os.mkdir(dir_)
    except FileExistsError:
        pass

    shutil.copytree(
        "examiner", f"{dir_}/examiner", ignore=shutil.ignore_patterns("*pycache*")
    )
    copy_and_insert_pylint_disable(read_requirements("requirements.txt"), dir_)

    # Can be used when pylint bug is fixed
    # for module in modules:
    # module_path = "build/examiner/" + module[1]
    # shutil.copytree(
    #     module[0],
    #     module_path,
    #     ignore=shutil.ignore_patterns("*pycache*")
    # )

    if make_archive:
        shutil.make_archive(
            f"{dir_}/examiner-" + src.__version__, "zip", "build/examiner"
        )


if __name__ == "__main__":
    build("build", True)
    build("test/python/.dbwebb/test")
