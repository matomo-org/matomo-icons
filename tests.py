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
import sys
from glob import glob
from subprocess import Popen, PIPE
from urllib.parse import urlparse

import yaml
from PIL import Image

ignored_source_files = [
    "src/flags/un.svg",
    "src/flags/gb-wls.svg",
    "src/flags/gb-sct.svg",
    "src/flags/gb-eng.svg",
    "src/flags/gb-nir.svg",
    "src/flags/es-ct.svg",
    "src/flags/xk.svg"
]

placeholder_icon_filenames = {
    "brand": "unk.png",
    "browsers": "UNK.png",
    "devices": "unknown.png",
    "os": "UNK.png",
    "searchEngines": "xx.png",
    "socials": "xx.png"
}

ignore_that_icon_isnt_square = [
    "dist/searchEngines/www.x-recherche.com.png",
    "dist/plugins/gears.png",
    "dist/brand/Landvo.png"
]
# @formatter:off
less_important_device_detector_icons = ['os|BMP', 'os|INF', 'os|MCD', 'os|MLD', 'os|MTK', 'os|RZD', 'os|SYS', 'os|S40', 'os|S60', 'os|SY3', 'os|WTV', 'browsers|AF', 'browsers|CX', 'browsers|CS', 'browsers|DB', 'browsers|DO', 'browsers|EB', 'browsers|LU', 'browsers|OD', 'browsers|SC', 'browsers|SN', 'browsers|SR', 'browsers|VB', 'browsers|WT', 'browsers|XI', 'brand|Ainol', 'brand|Airness', 'brand|Airties', 'brand|Allview', 'brand|Altech_UEC', 'brand|Amoi', 'brand|Arnova', 'brand|ARRIS', 'brand|Axxion', 'brand|Barnes_&_Noble', 'brand|BenQ-Siemens', 'brand|Bird', 'brand|Blackview', 'brand|Blu', 'brand|Bmobile', 'brand|Boway', 'brand|Bravis', 'brand|Brondi', 'brand|Bush', 'brand|Capitel', 'brand|Captiva', 'brand|Carrefour', 'brand|Casio', 'brand|Changhong', 'brand|China_Mobile', 'brand|Coby_Kyros', 'brand|Cowon', 'brand|Cube', 'brand|CUBOT', 'brand|Datang', 'brand|Dbtel', 'brand|Desay', 'brand|Dicam', 'brand|DNS', 'brand|Doogee', 'brand|Doov', 'brand|Dopod', 'brand|Dune_HD', 'brand|E-Boda', 'brand|EBEST', 'brand|ECS', 'brand|Elephone', 'brand|Energy_Sistem', 'brand|Ericy', 'brand|Eton', 'brand|Explay', 'brand|Ezio', 'brand|Ezze', 'brand|Fairphone', 'brand|Foxconn', 'brand|Garmin-Asus', 'brand|Gateway', 'brand|GOCLEVER', 'brand|Goly', 'brand|Grape', 'brand|Hasee', 'brand|Hi-Level', 'brand|Hisense', 'brand|Homtom', 'brand|Hosin', 'brand|i-Joy', 'brand|i-mate', 'brand|iBall', 'brand|iKoMo', 'brand|iNew', 'brand|Infinix', 'brand|Inkti', 'brand|Innostream', 'brand|Intex', 'brand|iOcean', 'brand|iTel', 'brand|Jiayu', 'brand|K-Touch', 'brand|Kiano', 'brand|Kingsun', 'brand|Komu', 'brand|Konka', 'brand|Koobee', 'brand|KOPO', 'brand|Koridy', 'brand|KT-Tech', 'brand|Kumai', 'brand|LCT', 'brand|LeEco', 'brand|Lemhoov', 'brand|Lenco', 'brand|Lexand', 'brand|Lexibook', 'brand|Lingwin', 'brand|Logicom', 'brand|M.T.T.', 'brand|Majestic', 'brand|Mecer', 'brand|Mediacom', 'brand|MEEG', 'brand|Memup', 'brand|MEU', 'brand|Miray', 'brand|MIXC', 'brand|MLLED', 'brand|Mobistel', 'brand|Modecom', 'brand|Mofut', 'brand|Mpman', 'brand|Netgear', 'brand|Newgen', 'brand|NextBook', 'brand|Noain', 'brand|Nomi', 'brand|Nous', 'brand|Opsson', 'brand|Ouki', 'brand|OUYA', 'brand|Overmax', 'brand|Oysters', 'brand|Pentagram', 'brand|phoneOne', 'brand|Pioneer', 'brand|Ployer', 'brand|Point_of_View', 'brand|Pomp', 'brand|Positivo', 'brand|PPTV', 'brand|Prestigio', 'brand|Primepad', 'brand|ProScan', 'brand|PULID', 'brand|Qilive', 'brand|Qtek', 'brand|Ramos', 'brand|RCA_Tablets', 'brand|Readboy', 'brand|Rikomagic', 'brand|Roku', 'brand|Rover', 'brand|Sanei', 'brand|Sendo', 'brand|Senseit', 'brand|Skyworth', 'brand|Smartisan', 'brand|Star', 'brand|Stonex', 'brand|Storex', 'brand|Sumvision', 'brand|SunVan', 'brand|SuperSonic', 'brand|Supra', 'brand|Symphony', 'brand|TB_Touch', 'brand|Telenor', 'brand|Tesco', 'brand|ThL', 'brand|TIANYU', 'brand|Top_House',  'brand|Toplux', 'brand|Trevi', 'brand|Turbo-X', 'brand|TVC', 'brand|Uniscope', 'brand|Unknown', 'brand|Unowhy', 'brand|UTStarcom', 'brand|Vastking', 'brand|Vinsoc', 'brand|Vitelcom', 'brand|Vizio', 'brand|VK_Mobile', 'brand|Voto', 'brand|Walton', 'brand|Web_TV', 'brand|WellcoM', 'brand|Wexler', 'brand|Wonu', 'brand|Xolo', 'brand|Ytone', 'brand|Yusun', 'brand|Zeemi', 'brand|Zuum']
# @formatter:on

build_script_regex = re.compile(r"rm [-rf]+ plugins/Morpheus/icons/(.*)")

min_image_size = 48

placeholder_icon_hash = "398a623a3b0b10eba6d1884b0ff1713ee12aeafaa8efaf67b60a4624f4dce48c"

searchEnginesFile = "vendor/matomo/searchengine-and-social-list/SearchEngines.yml"
socialsEnginesFile = "vendor/matomo/searchengine-and-social-list/Socials.yml"


def print_warning(string):
    print("\033[33;1m⚠\033[0m " + string)


def print_error(string):
    print("\033[31;1m⚠ " + string + "\033[0m")


def load_yaml(file):
    with open(file, 'r') as stream:
        return yaml.safe_load(stream)


def image_exists(pathslug):
    for filetype in ["svg", "png", "gif", "jpg", "ico"]:
        if os.path.isfile(pathslug + "." + filetype):
            return True
    return False


def test_if_all_icons_are_converted():
    global error
    for filetype in ["svg", "png", "gif", "jpg", "ico"]:
        for file in glob("src/**/*.{}".format(filetype)):
            abs_dirname, filename = os.path.split(file)
            code = os.path.splitext(filename)[0]
            distfolder = "dist/" + abs_dirname[4:]
            distfile = "{folder}/{code}.png".format(folder=distfolder, code=code)

            if not os.path.isfile(distfile) and file not in ignored_source_files:
                print_error("{file} is missing (From {source})".format(file=distfile, source=file))
                error = True

    return True


def test_if_source_for_images():
    global error
    for icontype in ["brand", "browsers", "os", "plugins", "SEO"]:
        for filetype in ["svg", "png", "gif", "jpg", "ico"]:
            for source_file in glob("src/{type}/*.{filetype}".format(type=icontype, filetype=filetype)):
                if not os.path.islink(source_file):
                    if not os.path.isfile(source_file + ".source") and "UNK" not in source_file:
                        print_error("Source is missing for {file}".format(file=source_file))
                        error = True


def test_if_all_symlinks_are_valid():
    global error
    for file in glob("src/**/*"):
        if os.path.islink(file) and not os.path.exists(file):
            print_error(
                "Symlink doesn't link to file (from {link} to {target}".format(link=file, target=os.readlink(file))
            )
            error = True


def test_if_placeholder_icon_exist():
    global error
    for folder, filename in placeholder_icon_filenames.items():
        file = "src/{folder}/{filename}".format(folder=folder, filename=filename)
        if not (os.path.isfile(file) and hashlib.sha256(open(file, "rb").read()).hexdigest() == placeholder_icon_hash):
            print_error("The placeholder icon {path} is missing or invalid".format(path=file))
            error = True


def test_if_icons_are_large_enough():
    # ignore searchEngines and socials
    for filetype in ["png", "gif", "jpg", "ico"]:
        for source_file in glob("src/*/*.{filetype}".format(filetype=filetype)):
            im = Image.open(source_file)
            if im.size[0] < min_image_size or im.size[1] < min_image_size:
                print_warning(
                    "{file} is smaller ({width}x{height}) that the target size ({target}x{target})".format(
                        file=source_file,
                        width=im.size[0],
                        height=im.size[1],
                        target=min_image_size
                    )
                )
            if filetype in ["jpg", "gif", "ico"]:
                print_warning("{file} is saved in a lossy image format ({filetype}). ".format(
                    file=source_file,
                    filetype=filetype
                ) + "Maybe try to find an PNG or SVG from another source.")


def test_if_dist_icons_are_square():
    global error
    for file in glob("dist/**/*.png"):
        if "flags" not in file:
            im = Image.open(file)
            if im.size[0] != im.size[1]:
                string = "{file} isn't square ({width}x{height})".format(file=file, width=im.size[0], height=im.size[1])
                if file not in ignore_that_icon_isnt_square:
                    error = True
                    print_error(string)
                else:
                    print_warning(string)


def test_if_build_script_is_deleting_all_unneeded_files():
    with open("tmp/piwik-package/scripts/build-package.sh") as f:
        build_script = f.read()
    global error
    deleted_files = []
    all_files = []
    for root, dirs, files in os.walk(".", topdown=False):
        for name in files:
            all_files.append(os.path.join(root, name))
        for name in dirs:
            all_files.append(os.path.join(root, name))
    for pattern in build_script_regex.findall(build_script):
        deleted_files.extend(glob(pattern))
    for file in all_files:
        if not any(s in file for s in deleted_files) and not (
                file.startswith("./dist") or file.startswith("./tmp") or file.startswith("./vendor")
                or file.startswith("./node_modules")
        ) and file != "./README.md":
            print_error("{file} should be deleted by the build script".format(file=file))
            error = True


def test_if_icons_are_indicated_to_be_improvable():
    for file in glob("src/**/*.todo"):
        print_warning("{icon} could be improved".format(icon=file[:-5]))


def look_for_search_and_social_icon(source, mode, outputdir):
    global error
    correct_files = []
    for i, element in source.items():
        if mode == "searchengines":
            search_engine = element[0]
            urls = search_engine["urls"]
        else:
            urls = element
        url = next((url for url in urls if "{}" not in url), False)
        url = urlparse("https://" + url).netloc

        if url and not image_exists(outputdir + url):
            print_error("icon for {icon} is missing".format(icon=url))
            error = True
        correct_files.append(url)
        # print(correct_files)
    for filetype in ["svg", "png", "gif", "jpg", "ico"]:
        for file in glob(outputdir + "*.{ext}".format(ext=filetype)):
            domain = os.path.splitext(os.path.basename(file))[0]
            if domain not in correct_files and domain != "xx":
                print_error("{file} is not necessary".format(file=file))
                error = True


def test_if_all_search_and_social_sites_have_an_icon():
    look_for_search_and_social_icon(load_yaml(searchEnginesFile), "searchengines", "src/searchEngines/")
    look_for_search_and_social_icon(load_yaml(socialsEnginesFile), "socials", "src/socials/")


def test_if_there_are_icons_for_all_device_detector_categories():
    global error
    process = Popen(["php", "devicedetector.php"], stdout=PIPE)
    (output, err) = process.communicate()
    process.wait()
    categories = json.loads(output)
    for name, category in categories.items():
        for code in category:
            if name == "brand":
                slug = category[code].replace(" ", "_")
            else:
                slug = code
            found = False
            for filetype in ["svg", "png", "gif", "jpg", "ico"]:
                if os.path.isfile("src/{type}/{slug}.{ext}".format(type=name, slug=slug, ext=filetype)):
                    found = True
            if not found:
                warning = "icon for {icon} missing (should be at src/{type}/{slug}.{{png|svg}})".format(
                    type=name, icon=category[code], slug=slug
                )
                if "|".join([name, slug]) in less_important_device_detector_icons:
                    print_warning(warning)
                else:
                    print_error(warning)
                    error = True


if __name__ == "__main__":
    error = False

    if "TRAVIS_PULL_REQUEST" not in os.environ or not os.environ["TRAVIS_PULL_REQUEST"]:
        test_if_all_icons_are_converted()

    test_if_source_for_images()
    test_if_all_symlinks_are_valid()
    test_if_placeholder_icon_exist()
    test_if_dist_icons_are_square()
    if "TRAVIS" in os.environ and os.environ["TRAVIS"]:  # collapse on travis
        print("travis_fold:start:improvable_icons")
        print("improvable icons: (click to expand)")
        test_if_there_are_icons_for_all_device_detector_categories()
        test_if_icons_are_indicated_to_be_improvable()
        test_if_icons_are_large_enough()
        print("travis_fold:end:improvable_icons")
        test_if_all_search_and_social_sites_have_an_icon()
        test_if_build_script_is_deleting_all_unneeded_files()
    else:
        test_if_there_are_icons_for_all_device_detector_categories()
        test_if_icons_are_indicated_to_be_improvable()
        test_if_icons_are_large_enough()
        test_if_all_search_and_social_sites_have_an_icon()
        test_if_build_script_is_deleting_all_unneeded_files()

    sys.exit(error)
