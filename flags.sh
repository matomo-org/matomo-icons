#!/bin/bash
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
    code=${origFilename%.*}
    distFile="${targetDir}/${code}.png"
    echo "$distFile"
    inkscape -f "$i" -h $height -e "$distFile"
    pngquant -f --ext .png -s 1 --skip-if-larger --quality 70-95 "$distFile"
done

inkscape -f "unk.flag.svg" -h $height -e "dist/flags/xx.png"
pngquant -f --ext .png -s 1 --skip-if-larger --quality 70-95 "dist/flags/xx.png"
inkscape -f "ti.flag.svg" -h $height -e "dist//flags/ti.png"
pngquant -f --ext .png -s 1 --skip-if-larger --quality 70-95 "dist//flags/ti.png"
