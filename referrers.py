import shutil
import sys

import requests
import yaml

MODE = "socials"

if MODE == "searchengines":
    yamlfile = "vendor/piwik/searchengine-and-social-list/SearchEngines.yml"
    outputdir = "src/Referrers/images/searchengines/"
elif MODE == "socials":
    yamlfile = "vendor/piwik/searchengine-and-social-list/Socials.yml"
    outputdir = "src/Referrers/images/socials/"
else:
    yamlfile = outputdir = False
    print("Invalid mode")
    exit(1)

with open(yamlfile, 'r') as stream:
    search_engines = yaml.load(stream)
try:
    finished = [line.rstrip('\n') for line in open('finished.txt')]
except FileNotFoundError:
    finished = []

for i, element in search_engines.items():
    if MODE == "searchengines":
        search_engine = element[0]
        urls = search_engine["urls"]
    else:
        urls = element
    for url in urls:
        if "{}" not in url and "/" not in url and url not in finished:
            print(url)
            try:
                offline = False
                r = requests.get("http://" + url, timeout=15)
                r.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print("http://" + url + "  " + str(e), file=sys.stderr)
                offline = True
            except requests.exceptions.ReadTimeout as e:
                print("http://" + url + "  " + "Timeout", file=sys.stderr)
                offline = True
            except requests.exceptions.TooManyRedirects as e:
                print("http://" + url + "  " + "Too many Redirects", file=sys.stderr)
                offline = True
            except requests.exceptions.ConnectionError as e:
                print("http://" + url + "  " + str(e), file=sys.stderr)
                offline = True
            except requests.exceptions.RequestException as e:
                print("http://" + url + "  " + str(e.args[0].reason), file=sys.stderr)
                offline = True

            if not offline:
                r = requests.get("http://" + url + "/favicon.ico", stream=True)
                if r.status_code == 200:
                    with open(outputdir + url + ".ico", 'wb') as f:
                        r.raw.decode_content = True
                        shutil.copyfileobj(r.raw, f)
            with open("finished.txt", "a") as myfile:
                myfile.write(url + "\n")
