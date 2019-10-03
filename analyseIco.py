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

import re
import subprocess
import sys

file = sys.argv[1]

output = subprocess.check_output("identify " + file, shell=True).decode()
icons = output.splitlines()

regex = r"\d+x\d+"
maxsize = 0
maxpos = 0
for i, file_line in enumerate(icons):
    resolution = re.findall(regex, file_line)[0]  # e.g. 16x16
    size = int(resolution.split("x")[0])  # e.g. 16
    # "1-bit"-images are not very helpful
    if size >= maxsize and " 1-bit" not in str(file_line):
        maxsize = size
        maxpos = i
print(maxpos)
