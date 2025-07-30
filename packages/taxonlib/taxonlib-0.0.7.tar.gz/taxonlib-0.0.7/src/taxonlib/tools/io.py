import json
import logging
import os
from typing import Optional, Tuple

import requests


class GbifApiTimeout(Exception):
    pass


default_gbif_cache_folder = os.path.join(os.path.dirname(__file__), "..", "gbif_cache")


def gbif_by_key(
    accepted_usage_key_,
    cache_folder: str = default_gbif_cache_folder,
):
    cache_path = get_cache_path(cache_folder, f"{accepted_usage_key_}")
    if cache_path is not None and os.path.exists(cache_path):
        j_taxon = json.load(open(cache_path))
    else:
        try:
            url = f"https://api.gbif.org/v1/species/{accepted_usage_key_}"
            j_taxon = requests.get(url).json()
        except requests.exceptions.ConnectTimeout:
            print(url)
            raise GbifApiTimeout()
        if cache_path is not None:
            json.dump(j_taxon, open(cache_path, "w"), indent=2)
    return j_taxon


path_replacements = {"/": "FORWARDSLASH", ".": "POINT"}


def get_cache_path(cache_folder, filename):
    cache_path = None
    if cache_folder is not None:
        os.makedirs(cache_folder, exist_ok=True)
        for from_, to_ in path_replacements.items():
            filename = filename.replace(from_, to_)
        cache_path = os.path.join(cache_folder, filename + ".json")
    return cache_path


def change_path_end(path, postfix, extension):
    # TODO: this is copied from Naturalis AI, find a way to share the code without directly referring to Naturalis AI
    if "." not in extension:
        extension = "." + extension
    return os.path.join(
        os.path.dirname(path),
        os.path.splitext(os.path.basename(path))[0] + postfix + extension,
    )


def get_logger(filename: str, mode: str = "a") -> logging.Logger:
    """
    Enable file and console logging to 'filename'
    :param filename:
    :param mode: file mode ('a','w', etc.) for log file
    :return:
    """
    logger = logging.getLogger("")
    logger.setLevel(logging.INFO)
    logger.handlers = []
    formatter = logging.Formatter("%(asctime)s %(message)s")
    file_logger = logging.FileHandler(filename, mode=mode)
    file_logger.setFormatter(formatter)
    file_logger.setLevel(logging.DEBUG)
    logger.addHandler(file_logger)
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console.setLevel(logging.INFO)
    logger.addHandler(console)

    return logger


def gbif_search_taxon(
    kingdom: str,
    search_name: str,
    verbose: bool,
    parent_tuple: tuple[str, str] | None = None,
    cache_folder: str = default_gbif_cache_folder,
):
    cache_path = get_cache_path(cache_folder, f"{search_name}_{kingdom}")
    if cache_path is not None and os.path.exists(cache_path):
        j_taxon = json.load(open(cache_path))
    else:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
        }
        if kingdom == "Bacteria":
            kingdom = "Animalia"
        gbif_url = f"https://api.gbif.org/v1/species/match?verbose=true&name={search_name}&kingdom={kingdom}"
        if parent_tuple is not None:
            gbif_url += f"&{parent_tuple[0]}={parent_tuple[1]}"
        if verbose:
            print("gbif_url", gbif_url)
        try:
            j_taxon = requests.get(gbif_url, timeout=(10, 10), headers=headers).json()
        except requests.exceptions.ConnectTimeout:
            raise GbifApiTimeout("gbif_url", gbif_url, "failed due to ConnectTimeout")
        except requests.exceptions.ConnectionError:
            raise GbifApiTimeout("gbif_url", gbif_url, "failed due to ConnectionError")

        if cache_path is not None:
            json.dump(j_taxon, open(cache_path, "w"), indent=2)
    return j_taxon
