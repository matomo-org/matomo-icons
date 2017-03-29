#!/bin/bash
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
set -x
height=48
targetDir="dist/flags"
if [ ! -d "$targetDir" ]
then
    mkdir -p "$targetDir"
fi

for i in src/flags/*.svg; do
    echo "$i"
    origFilename=$(basename "$i")
    code="${origFilename%.*}"
    distFile="${targetDir}/${code}.png"
    echo "$distFile"
    inkscape -f "$i" -h $height -e "$distFile"
    pngquant -f --ext .png -s 1 --skip-if-larger --quality 70-95 "$distFile"
done

inkscape -f "unk.flag.svg" -h $height -e "dist/flags/xx.png"
pngquant -f --ext .png -s 1 --skip-if-larger --quality 70-95 "dist/flags/xx.png"
inkscape -f "ti.flag.svg" -h $height -e "dist//flags/ti.png"
pngquant -f --ext .png -s 1 --skip-if-larger --quality 70-95 "dist//flags/ti.png"

for i in ac cp dg ea eu fx ic su ta uk an bu cs nt sf tp yu zr a1 a2 ap o1 cat
do
    icon="${targetDir}/${i}.png"
    if [ ! -f "$icon" ]
    then
        echo -e "\033[31mWarning: No flag for $i, using default\033[0m"
        cp "dist/flags/xx.png" "$icon"
    fi
done

rm ${targetDir}/gb-*
rm ${targetDir}/un.png
