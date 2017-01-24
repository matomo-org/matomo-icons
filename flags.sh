#!/bin/bash
set -x
height=48
targetDir="dist/UserCountry/images/flags/"
if [ ! -d "$targetDir" ]
then
    mkdir -p "$targetDir"
fi

for i in src/UserCountry/images/flags/*.svg; do
    echo "$i"
    origFilename=$(basename "$i")
    code=${origFilename%.*}
    distFile="${targetDir}/${code}.png"
    echo "$distFile"
    inkscape -f "$i" -h $height -e "$distFile"
    pngquant -f --ext .png -s 1 --skip-if-larger --quality 70-95 "$distFile"
done

inkscape -f "unk.flag.svg" -h $height -e "dist/UserCountry/images/flags/xx.png"
pngquant -f --ext .png -s 1 --skip-if-larger --quality 70-95 "dist/UserCountry/images/flags/xx.png"
