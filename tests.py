#!/usr/bin/env python3
# Copyright (C) 2017 Lukas Winkler
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Iterator, Iterable
from urllib.parse import urlparse

import yaml
from PIL import Image

build_script_regex = re.compile(r"rm [-rf]+ plugins/Morpheus/icons/(.*)")

min_image_size = 48

placeholder_icon_hash = "398a623a3b0b10eba6d1884b0ff1713ee12aeafaa8efaf67b60a4624f4dce48c"

searchEnginesFile = Path("vendor/matomo/searchengine-and-social-list/SearchEngines.yml")
socialsEnginesFile = Path("vendor/matomo/searchengine-and-social-list/Socials.yml")
build_script_file = Path("tmp/piwik-package/scripts/build-package.sh")

src = Path("src/")
dist: Path = Path("dist/")


def print_warning(string: str) -> None:
    print("\033[33;1m⚠\033[0m " + string)


def print_error(string: str) -> None:
    print("\033[31;1m⚠ " + string + "\033[0m")


def load_yaml(file: Path):
    with file.open() as stream:
        return yaml.safe_load(stream)


def image_exists(pathslug: Path) -> bool:
    for filetype in ["svg", "png", "gif", "jpg", "ico"]:
        if pathslug.with_suffix(pathslug.suffix + f".{filetype}").exists():
            return True
    return False


def walk(path: Path) -> Iterator[Path]:
    for p in path.iterdir():
        if p.is_dir():
            yield p
            yield from walk(p)
            continue
        yield p.resolve()


def test_if_all_icons_are_converted(ignored_source_files) -> None:
    global error
    for filetype in ["svg", "png", "gif", "jpg", "ico"]:
        for file in src.glob(f"**/*.{filetype}"):
            distfile = Path("dist/") / Path(*file.parts[1:]).with_suffix(".png")

            if not distfile.exists() and file not in ignored_source_files:
                print_error(f"{distfile} is missing (From {file})")
                error = True


def test_if_source_for_images() -> None:
    global error
    for icontype in ["brand", "browsers", "os", "plugins", "SEO"]:
        for filetype in ["svg", "png", "gif", "jpg", "ico"]:
            for source_file in (src / icontype).glob(f"*.{filetype}"):
                if (
                        not source_file.is_symlink()
                        and not source_file.with_suffix(source_file.suffix + ".source")
                        and "UNK" not in source_file
                ):
                    print_error(f"Source is missing for {source_file}")
                    error = True


def test_if_all_symlinks_are_valid() -> None:
    global error
    for file in src.glob("**/*"):
        if file.is_symlink():
            target = file.resolve()
            if not target.exists():
                print_error(f"Symlink doesn't link to file (from {file} to {target} ({file.readlink()}))")
                error = True


def test_if_placeholder_icon_exist(placeholder_icon_filenames: Dict[str, str]) -> None:
    global error
    for folder, filename in placeholder_icon_filenames.items():
        file = src / folder / filename
        if not (file.exists() and hashlib.sha256(file.read_bytes()).hexdigest() == placeholder_icon_hash):
            print_error(f"The placeholder icon {file} is missing or invalid")
            error = True


def test_if_icons_are_large_enough() -> None:
    # ignore searchEngines and socials
    for filetype in ["png", "gif", "jpg", "ico"]:
        for source_file in src.glob(f"*/*.{filetype}"):
            im = Image.open(source_file)
            if im.size[0] < min_image_size or im.size[1] < min_image_size:
                width, height = im.size
                print_warning(
                    f"{source_file} is smaller ({width}x{height}) that the target size ({min_image_size}x{min_image_size})"
                )
            if filetype in ["jpg", "gif", "ico"]:
                print_warning(
                    f"{source_file} is saved in a lossy image format ({filetype}). "
                    "Maybe try to find an PNG or SVG from another source."
                )


def test_if_dist_icons_are_square(ignore_that_icon_isnt_square: List[str]) -> None:
    global error
    for file in dist.glob("**/*.png"):
        if (dist / "flags") not in file.parents:
            im = Image.open(file)
            width, height = im.size
            if width != height:
                string = f"{file} isn't square ({width}x{height})"
                if str(file) not in ignore_that_icon_isnt_square:
                    error = True
                    print_error(string)
                else:
                    print_warning(string)


def is_in_allowed_dir(file: Path) -> bool:
    allowed_dirs = [dist, Path("node_modules"), Path("tmp"), Path("vendor"), Path(".idea")]
    for dir in allowed_dirs:
        dir = dir.resolve()
        if dir == file:
            return True
        if dir in file.parents:
            return True
    return False


def is_deleted(file: Path, deleted_files: Iterable[Path]) -> bool:
    # print(file, deleted_files)
    for del_file in deleted_files:
        if del_file == file:
            return True
        if del_file in file.parents:
            return True
    return False


def test_if_build_script_is_deleting_all_unneeded_files() -> None:
    global error
    build_script = build_script_file.read_text()
    deleted_files = set()
    all_files = set(walk(Path(".").resolve()))
    for pattern in build_script_regex.findall(build_script):
        deleted_files.update(Path(".").resolve().glob(pattern))
    for file in all_files:
        if is_deleted(file, deleted_files):
            continue
        if is_in_allowed_dir(file):
            continue
        if file == Path("README.md").resolve():
            continue
        print_error(f"{file} should be deleted by the build script")
        error = True


def test_if_icons_are_indicated_to_be_improvable() -> None:
    for file in src.glob("**/*.todo"):
        print_warning(f"{str(file)[:-5]} could be improved")


def look_for_search_and_social_icon(source, mode, outputdir: Path) -> None:
    global error
    correct_files = set()
    for i, element in source.items():
        if mode == "searchengines":
            search_engine = element[0]
            urls = search_engine["urls"]
        else:
            urls = element
        url = next((url for url in urls if "{}" not in url), False)
        url = urlparse("https://" + url).netloc
        if url and not image_exists(outputdir / url):
            print_error(f"icon for {url} is missing")
            error = True
        correct_files.add(url)
    for filetype in ["svg", "png", "gif", "jpg", "ico"]:
        for file in outputdir.glob(f"*.{filetype}"):
            domain = file.stem
            if domain not in correct_files and domain != "xx":
                print_error(f"{file} is not necessary")
                error = True


def test_if_all_search_and_social_sites_have_an_icon() -> None:
    look_for_search_and_social_icon(load_yaml(searchEnginesFile), "searchengines", Path("src/searchEngines/"))
    look_for_search_and_social_icon(load_yaml(socialsEnginesFile), "socials", Path("src/socials/"))


def test_if_there_are_icons_for_all_device_detector_categories(
        less_important_device_detector_icons: Dict[str, List[str]]
) -> None:
    global error
    output = subprocess.run(["php", "devicedetector.php"], capture_output=True)
    regex = re.compile(r"[^a-z0-9_\-]+", re.IGNORECASE)
    categories = json.loads(output.stdout)
    for icontype, category in categories.items():
        for code in category:
            if icontype == "brand":
                slug = regex.sub("_", category[code])
            else:
                slug = code
            found = False
            for filetype in ["svg", "png", "gif", "jpg", "ico"]:
                file = Path(f"src/{icontype}/{slug}.{filetype}")
                if file.exists():
                    found = True
                    break
            if not found:
                warning = f"icon for {category[code]} missing (should be at src/{icontype}/{slug}.{{png|svg}})"
                if slug in less_important_device_detector_icons[icontype]:
                    print_warning(warning)
                else:
                    print_error(warning)
                    # error = True


if __name__ == "__main__":
    error = False

    ignore = load_yaml(Path("tests-ignore.yml"))

    if "TRAVIS_PULL_REQUEST" not in os.environ or not os.environ["TRAVIS_PULL_REQUEST"]:
        test_if_all_icons_are_converted(ignore["ignored_source_files"])

    test_if_source_for_images()
    test_if_all_symlinks_are_valid()
    test_if_placeholder_icon_exist(ignore["placeholder_icon_filenames"])
    test_if_dist_icons_are_square(ignore["ignore_that_icon_isnt_square"])
    travis = "TRAVIS" in os.environ and os.environ["TRAVIS"]  # collapse on travis
    if travis:
        print("travis_fold:start:improvable_icons")
        print("improvable icons: (click to expand)")
    test_if_there_are_icons_for_all_device_detector_categories(ignore["less_important_device_detector_icons"])
    test_if_icons_are_indicated_to_be_improvable()
    test_if_icons_are_large_enough()
    if travis:
        print("travis_fold:end:improvable_icons")
    test_if_all_search_and_social_sites_have_an_icon()
    test_if_build_script_is_deleting_all_unneeded_files()

    sys.exit(error)
