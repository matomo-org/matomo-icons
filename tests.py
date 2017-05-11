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
from glob import glob
import os
import sys
from PIL import Image

ignored_source_files = [
    "src/flags/un.svg",
    "src/flags/gb-wls.svg",
    "src/flags/gb-sct.svg",
    "src/flags/gb-eng.svg",
    "src/flags/gb-nir.svg"
]

placeholder_icon_filenames = {
    "brand": "unk.png",
    "browsers": "UNK.png",
    "devices": "unknown.png",
    "os": "UNK.png",
    "searchEngines": "xx.png",
    "socials": "xx.png"
}

min_image_size = 48

placeholder_icon_hash = "398a623a3b0b10eba6d1884b0ff1713ee12aeafaa8efaf67b60a4624f4dce48c"


def test_if_all_icons_are_converted():
    global error
    for filetype in ["svg", "png", "gif", "jpg", "ico"]:
        for file in glob("src/**/*.{}".format(filetype)):
            abs_dirname, filename = os.path.split(file)
            code = os.path.splitext(filename)[0]
            distfolder = "dist/" + abs_dirname[4:]
            distfile = "{folder}/{code}.png".format(folder=distfolder, code=code)

            if not os.path.isfile(distfile) and file not in ignored_source_files:
                print("{file} is missing (From {source})".format(file=distfile, source=file))
                error = True

    return True


def test_if_source_for_images():
    global error
    for icontype in ["brand", "browsers", "os", "plugins", "SEO"]:
        for filetype in ["svg", "png", "gif", "jpg", "ico"]:
            for source_file in glob("src/{type}/*.{filetype}".format(type=icontype, filetype=filetype)):
                if not os.path.islink(source_file):
                    if not os.path.isfile(source_file + ".source") and "UNK" not in source_file:
                        print("Source is missing for {file}".format(file=source_file))
                        error = True


def test_if_all_symlinks_are_valid():
    global error
    for file in glob("src/**/*"):
        if os.path.islink(file) and not os.path.exists(file):
            print(
                "Symlink doesn't link to file (from {link} to {target}".format(link=file, target=os.readlink(file))
            )
            error = True


def test_if_placeholder_icon_exist():
    global error
    for folder, filename in placeholder_icon_filenames.items():
        file = "src/{folder}/{filename}".format(folder=folder, filename=filename)
        if not (os.path.isfile(file) and hashlib.sha256(open(file, "rb").read()).hexdigest() == placeholder_icon_hash):
            print("The placeholder icon {path} is missing or invalid".format(path=file))
            error = True


def test_if_icons_are_large_enough():
    # ignore searchEngines and socials
    for icontype in ["brand", "browsers", "devices", "flags", "os", "plugins", "SEO"]:
        for filetype in ["png", "gif", "jpg", "ico"]:
            for source_file in glob("src/{type}/*.{filetype}".format(type=icontype, filetype=filetype)):
                im = Image.open(source_file)
                if im.size[0] < min_image_size or im.size[1] < min_image_size:
                    print(
                        "{file} is smaller ({width}x{height}) that the target size ({target}x{target})".format(
                            file=source_file,
                            width=im.size[0],
                            height=im.size[1],
                            target=min_image_size
                        )
                    )
                if filetype in ["jpg", "gif", "ico"]:
                    print("{file} is saved in a lossy image format ({filetype}). ".format(
                        file=source_file,
                        filetype=filetype
                    ) + "Maybe try to find an PNG or SVG from another source.")


if __name__ == "__main__":
    error = False

    if "TRAVIS_PULL_REQUEST" not in os.environ or not os.environ["TRAVIS_PULL_REQUEST"]:
        test_if_all_icons_are_converted()

    test_if_source_for_images()
    test_if_all_symlinks_are_valid()
    test_if_placeholder_icon_exist()
    if "TRAVIS" in os.environ and os.environ["TRAVIS"]:  # collapse on travis
        print("travis_fold:start:small_icons")
        print("improvable icons: (click to expand)")
        test_if_icons_are_large_enough()
        print("travis_fold:end:small_icons")
    else:
        test_if_icons_are_large_enough()
    sys.exit(error)
