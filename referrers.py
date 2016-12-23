import shutil
import sys

import urllib.parse
import requests
import yaml
from bs4 import BeautifulSoup

MODE = "searchengines"

if MODE == "searchengines":
    yamlfile = "vendor/piwik/searchengine-and-social-list/SearchEngines.yml"
    outputdir = "src/Referrers/images/searchEngines/"
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
                soup = BeautifulSoup(r.content, "html.parser")
                favicon_element = soup.find("link", rel="shortcut icon")
                if favicon_element and "href" in favicon_element:
                    favicon_path = favicon_element['href']
                else:
                    favicon_path = "/favicon.ico"

                print(favicon_path)
                # Works with relative and absolute favicon_paths:
                favicon_url = urllib.parse.urljoin("http://" + url, favicon_path)
                print(favicon_url)
                try:
                    r = requests.get(favicon_url, stream=True)
                    if r.status_code == 200:
                        with open(outputdir + url + ".ico", 'wb') as f:
                            r.raw.decode_content = True
                            shutil.copyfileobj(r.raw, f)

                except requests.exceptions.ConnectionError:
                    print("Error while downloading favicon")
            with open("finished.txt", "a") as myfile:
                myfile.write(url + "\n")
