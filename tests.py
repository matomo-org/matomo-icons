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
import os

import glob

import sys

ignored_source_files = [
    "src/flags/un.svg",
    "src/flags/gb-wls.svg",
    "src/flags/gb-sct.svg",
    "src/flags/gb-eng.svg",
    "src/flags/gb-nir.svg"
]


def test_if_all_icons_are_converted():
    global error
    source_files = []
    for filetype in ["svg", "png", "gif", "jpg", "ico"]:
        source_files += glob.glob("src/**/*.{}".format(filetype))

    for file in source_files:
        abs_dirname, filename = os.path.split(file)
        code = os.path.splitext(filename)[0]
        distfolder = "dist/" + abs_dirname[4:]
        distfile = "{folder}/{code}.png".format(folder=distfolder, code=code)

        if not os.path.isfile(distfile) and file not in ignored_source_files:
            print("{file} is missing (From {source})".format(file=distfile, source=file))
            error = True

    return True


if __name__ == '__main__':
    error = False

    if 'TRAVIS_PULL_REQUEST' not in os.environ or not os.environ['TRAVIS_PULL_REQUEST']:
        test_if_all_icons_are_converted()

    sys.exit(error)
