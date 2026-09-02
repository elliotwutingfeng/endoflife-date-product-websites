"""Extract product websites from the endoflife.date API
and write them to a .txt allowlist
"""

import asyncio
import datetime
import ipaddress
import logging
import re
import socket

import httpx
import tldextract

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format="%(message)s")


def current_datetime_str() -> str:
    """Current time's datetime string in UTC

    Returns:
        str: Timestamp in strftime format "%d_%b_%Y_%H_%M_%S-UTC".
    """
    return datetime.datetime.now(datetime.UTC).strftime("%d_%b_%Y_%H_%M_%S-UTC")


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


async def extract_urls() -> set[str]:
    """Extract product websites from the endoflife.date API

    Returns:
        set[str]: Unique product URLs.
    """
    async with httpx.AsyncClient() as client:
        res: httpx.Response = await client.get(
            "https://endoflife.date/api/v1/products/full", timeout=30
        )
        res.raise_for_status()
        products_data = res.json()
        if not isinstance(products_data, dict):
            raise TypeError("Expected products_full endpoint to return dict")
        result = products_data.get("result")
        if not isinstance(result, list):
            raise TypeError("Expected 'result' to be a list")
        urls: set[str] = set()
        for product in result:
            if not isinstance(product, dict):
                continue
            product_releases = product.get("releases")
            if not isinstance(product_releases, list):
                continue
            for release in product_releases:
                if (
                    isinstance(release, dict)
                    and isinstance(release.get("latest"), dict)
                    and isinstance(release["latest"].get("link"), str)
                ):
                    urls.add(release["latest"]["link"])
        return urls


if __name__ == "__main__":
    urls: set[str] = asyncio.run(extract_urls())
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
            except OSError:
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
