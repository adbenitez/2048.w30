#!/usr/bin/env python3
import argparse
import os
import shutil

import htmlmin
import lesscpy
from jsmin import jsmin


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="App Builder",
    )
    parser.add_argument(
        "-n",
        "--name",
        default=os.path.basename(os.path.dirname(os.path.abspath(__file__))),
        help="App package's base name",
    )

    return parser


def size_fmt(num: float) -> str:
    suffix = "B"
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, "Yi", suffix)


if __name__ == "__main__":
    args = get_parser().parse_args()
    app_archive = args.name if args.name.endswith(".xdc") else f"{args.name}.xdc"

    # CLEAN
    shutil.rmtree("build", ignore_errors=True)
    os.makedirs("build/js")
    os.makedirs("build/css")
    if os.path.exists(app_archive):
        os.remove(app_archive)

    # ADD JS
    paths = [
        "js/animframe_polyfill.js",
        "js/application.js",
        "js/bind_polyfill.js",
        "js/classlist_polyfill.js",
        "js/game_manager.js",
        "js/grid.js",
        "js/html_actuator.js",
        "js/keyboard_input_manager.js",
        "js/tile.js",
    ]
    for path in paths:
        with open(path) as src:
            with open(f"build/{path}", "w") as dest:
                dest.write(jsmin(src.read()).replace("\n", ";"))

    # ADD CSS
    paths = [
        "css/main.css",
    ]
    for path in paths:
        with open(path) as src:
            with open(f"build/{path}", "w") as dest:
                dest.write(lesscpy.compile(src, minify=True, xminify=True))

    # ADD HTML
    with open("index.html") as src:
        with open("build/index.html", "w") as dest:
            dest.write(htmlmin.minify(src.read()))

    # ADD METADATA
    paths = [
        "manifest.toml",
        "icon.png",
    ]
    for path in paths:
        shutil.copyfile(f"{path}", f"build/{path}")

    project_root = os.path.abspath(".")
    os.chdir("build")
    shutil.make_archive(f"{project_root}/{app_archive}", "zip")
    os.chdir(project_root)
    os.rename(f"{app_archive}.zip", app_archive)
    shutil.copyfile("webxdc.js", "build/webxdc.js")

    with open(app_archive, "rb") as file:
        size = len(file.read())
    print(f"App saved as: {app_archive} ({size_fmt(size)})")