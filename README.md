# endoflife.date product websites

![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)

[![LICENSE](https://img.shields.io/badge/LICENSE-BSD--3--CLAUSE-GREEN?style=for-the-badge)](LICENSE)
[![scraper](https://img.shields.io/github/actions/workflow/status/elliotwutingfeng/endoflife-date-product-websites/scraper.yml?branch=main&label=SCRAPER&style=for-the-badge)](https://github.com/elliotwutingfeng/endoflife-date-product-websites/actions/workflows/scraper.yml)
![Total Allowlist FQDNs](https://tokei-rs.onrender.com/b1/github/elliotwutingfeng/endoflife-date-product-websites?label=Total%20Allowlist%20FQDNs&style=for-the-badge)

Machine-readable `.txt` allowlist of websites belonging to products listed by the [endoflife.date](https://endoflife.date) website, updated once a day.

Data is sourced from the [endoflife.date API](https://endoflife.date/docs/api).

**Disclaimer:** _This project is not sponsored, endorsed, or otherwise affiliated with endoflife.date._

## Allowlist download

| File | Download |
|:-:|:-:|
| urls.txt | [:floppy_disk:](urls.txt?raw=true) |
| urls-pihole.txt | [:floppy_disk:](urls-pihole.txt?raw=true) |
| ips.txt | [:floppy_disk:](ips.txt?raw=true) |

## Requirements

- Python 3.12+

## Setup instructions

`git clone` and `cd` into the project directory, then run the following

```bash
python3 -m venv venv
venv/bin/python3 -m pip install --upgrade pip
venv/bin/python3 -m pip install -r requirements.txt
```

## Usage

```bash
venv/bin/python3 scraper.py
```

## Libraries/Frameworks used

- [tldextract](https://github.com/john-kurkowski/tldextract)
