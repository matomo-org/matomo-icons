# Piwik-Icons

[![Build Status](https://travis-ci.org/piwik/piwik-icons.svg?branch=master)](https://travis-ci.org/piwik/piwik-icons)

This reposistory provides the source files for the icons in [piwik](https://github.com/piwik/piwik) and the scripts used to resize them to a common size.

## Contributing

An icon is missing or you have a better one? Create a [new issue](https://github.com/piwik/piwik-icons/issues/new) or, even better, open a pull request.

All source files except those in `devices`, `flags`, `searchEngines` and `socials` need to have a second file called `iconname.ext.source` that mentions where the image is from.

### Naming conventions

| icon type | example | possible names |
| --------- | ------- | ----------- |
|brand|*Apple*| *Device detection* in Piwik Administration page|
|browsers|*FF*|https://github.com/piwik/device-detector/blob/master/Parser/Client/Browser.php#L29 |
|devices|*smartphone*| *Device detection* in Piwik Administration page|
|flags|*at*| all except *un* and *gb-** |
|os|*WIN*|https://github.com/piwik/device-detector/blob/master/Parser/OperatingSystem.php#L30 |
|plugins|*flash*|https://github.com/piwik/piwik/blob/3.x-dev/plugins/DevicePlugins/Visitor.php#L26 |
|searchEngines|*google.com*|https://github.com/piwik/searchengine-and-social-list/blob/master/SearchEngines.yml |
|SEO|*bing.com*|https://github.com/piwik/piwik/tree/3.x-dev/plugins/SEO |
|socials|*facebook.com*|https://github.com/piwik/searchengine-and-social-list/blob/master/Socials.yml |

### File Formats

Ideally all source files should be SVGs or high resolution (>100px) PNGs. As this is not always possible, JPGs, GIFs and (even multiresolution) ICOs are supported.
