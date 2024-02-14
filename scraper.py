"""Extract product websites from the endoflife.date API
and write them to a .txt allowlist
"""

import ipaddress
import logging
import re
import socket
import time
from datetime import datetime

import requests
import tldextract

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format="%(message)s")


def current_datetime_str() -> str:
    """Current time's datetime string in UTC

    Returns:
        str: Timestamp in strftime format "%d_%b_%Y_%H_%M_%S-UTC".
    """
    return datetime.utcnow().strftime("%d_%b_%Y_%H_%M_%S-UTC")


def clean_url(url: str) -> str:
    """Remove zero width spaces, leading/trailing whitespaces, trailing slashes,
    and URL prefixes from a URL

    Args:
        url (str): URL.

    Returns:
        str: URL without zero width spaces, leading/trailing whitespaces, trailing slashes,
    and URL prefixes.
    """
    removed_zero_width_spaces = re.sub(r"[\u200B-\u200D\uFEFF]", "", url)
    removed_leading_and_trailing_whitespaces = removed_zero_width_spaces.strip()
    removed_trailing_slashes = removed_leading_and_trailing_whitespaces.rstrip("/")
    removed_https = re.sub(r"^[Hh][Tt][Tt][Pp][Ss]:\/\/", "", removed_trailing_slashes)
    removed_http = re.sub(r"^[Hh][Tt][Tt][Pp]:\/\/", "", removed_https)

    return removed_http


def extract_urls() -> set[str]:
    """Extract product websites from the endoflife.date API

    Returns:
        set[str]: Unique product URLs.
    """
    url_column_names: list[str] = ["TE%sN528" % str(i + 1).zfill(2) for i in range(10)]

    try:
        res: requests.Response = requests.get(
            "https://endoflife.date/api/all.json", timeout=30
        )
        res.raise_for_status()
        products = res.json()
        if not isinstance(products, list) or not all(
            map(lambda product: isinstance(product, str), products)
        ):
            raise ValueError("Expected all.json to be of type list[str]")

        urls: set[str] = set()

        for product in products:
            time.sleep(0.25)  # Rate limit
            res = requests.get(f"https://endoflife.date/api/{product}.json", timeout=30)
            if res.status_code != 200:
                logger.warning("%s | HTTP Status: %d", product, res.status_code)
                continue
            cycles: list[dict] = res.json()
            for cycle in cycles:
                url = cycle.get("link", None)
                if isinstance(url, str):
                    urls.add(url)
        return urls
    except Exception as error:
        logger.error(error)
        return set()


if __name__ == "__main__":
    urls: set[str] = extract_urls()
    ips: set[str] = set()
    non_ips: set[str] = set()
    fqdns: set[str] = set()

    if not urls:
        raise ValueError("Failed to scrape URLs")
    for url in urls:
        res = tldextract.extract(url)
        domain, fqdn = res.domain, res.fqdn
        if domain and not fqdn:
            # Possible IPv4 Address
            try:
                socket.inet_pton(socket.AF_INET, domain)
                ips.add(domain)
            except socket.error:
                # Is invalid URL and invalid IP -> skip
                pass
        elif fqdn:
            non_ips.add(url)
            fqdns.add(fqdn.lower())

    if not non_ips and not ips:
        logger.error("No content available for allowlists.")
    else:
        non_ips_timestamp: str = current_datetime_str()
        non_ips_filename = "urls.txt"
        with open(non_ips_filename, "w") as f:
            f.writelines("\n".join(sorted(non_ips)))
            logger.info(
                "%d non-IPs written to %s at %s",
                len(non_ips),
                non_ips_filename,
                non_ips_timestamp,
            )

        ips_timestamp: str = current_datetime_str()
        ips_filename = "ips.txt"
        with open(ips_filename, "w") as f:
            f.writelines("\n".join(sorted(ips, key=ipaddress.IPv4Address)))
            logger.info(
                "%d IPs written to %s at %s", len(ips), ips_filename, ips_timestamp
            )

        fqdns_timestamp: str = current_datetime_str()
        fqdns_filename = "urls-pihole.txt"
        with open(fqdns_filename, "w") as f:
            f.writelines("\n".join(sorted(fqdns)))
            logger.info(
                "%d FQDNs written to %s at %s",
                len(fqdns),
                fqdns_filename,
                fqdns_timestamp,
            )
