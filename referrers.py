import shutil
import sys
import urllib.parse
import os.path
import requests
import yaml
from bs4 import BeautifulSoup


def load_yaml(file):
    with open(file, 'r') as stream:
        return yaml.load(stream)


def download_favicon(homepage_html, url, target_file):
    """
    Detect favicon if linked via "<link rel="shortcut icon" href="/favicon.ico">"
    otherwise assume /favicon.ico
    """
    print(url, target_file)
    soup = BeautifulSoup(homepage_html, "html.parser")
    favicon_element = soup.find("link", rel="shortcut icon")
    if favicon_element and favicon_element.has_attr("href"):
        favicon_path = favicon_element['href']
    elif soup.find("link", rel="icon") and soup.find("link", rel="icon").has_attr("href"):
        # some sites don't use "shortcut icon" for favicon
        # in this case we take the first other icon and hope it fits
        favicon_path = soup.find("link", rel="icon")["href"]
    else:
        favicon_path = "/favicon.ico"
    print(favicon_path)
    # Works with relative and absolute favicon_paths:
    favicon_url = urllib.parse.urljoin("http://" + url, favicon_path)
    print(favicon_url)
    try:
        r = requests.get(favicon_url, stream=True)
        if r.status_code == 200:
            with open(outputdir + target_file + ".ico", 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
                return True

    except (
            requests.exceptions.ConnectionError,
            requests.exceptions.InvalidSchema,
            requests.exceptions.TooManyRedirects):
        print("Error while downloading favicon")


def main(search_engines):
    for i, element in search_engines.items():
        if MODE == "searchengines":
            search_engine = element[0]
            urls = search_engine["urls"]
        else:
            urls = element
        first_url = None
        success = False
        for url in urls:
            if "{}" not in url and "/" not in url:
                if first_url is None:
                    first_url = url
                print(url)
                if not os.path.isfile(outputdir + first_url + ".ico"):
                    try:
                        offline = False
                        r = requests.get("http://" + url, timeout=15)
                        r.raise_for_status()
                    except requests.exceptions.ReadTimeout as e:
                        print("http://" + url + "  " + "Timeout", file=sys.stderr)
                        offline = True
                    except requests.exceptions.TooManyRedirects as e:
                        print("http://" + url + "  " + "Too many Redirects", file=sys.stderr)
                        offline = True
                    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError,
                            requests.exceptions.TooManyRedirects) as e:
                        print("http://" + url + "  " + str(e), file=sys.stderr)
                        offline = True
                    except requests.exceptions.RequestException as e:
                        print("http://" + url + "  " + str(e.args[0].reason), file=sys.stderr)
                        offline = True

                    if not offline:
                        success = download_favicon(r.content, url, first_url)
                        if success:
                            break
                else:
                    print("file already downloaded")


if __name__ == "__main__":
    MODE = sys.argv[1] if len(sys.argv) >= 2 else ""

    if MODE == "searchengines":
        yamlfile = "vendor/piwik/searchengine-and-social-list/SearchEngines.yml"
        outputdir = "src/Referrers/images/searchEngines/"
    elif MODE == "socials":
        yamlfile = "vendor/piwik/searchengine-and-social-list/Socials.yml"
        outputdir = "src/Referrers/images/socials/"
    else:
        yamlfile = outputdir = False
        print('Invalid mode. Valid modes: "searchengines" or "socials"')
        exit(1)
    try:
        finished = [line.rstrip('\n') for line in open('finished.txt')]
    except FileNotFoundError:
        finished = []

    main(load_yaml(yamlfile))
