"""Module implements utilitary functions shared by download
package"""
from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from tempfile import NamedTemporaryFile, _TemporaryFileWrapper

import requests


def get_data(tar_url: str,
             target: str,
             processor: Callable[[_TemporaryFileWrapper[bytes], str], Path]) -> str:
    """Function downloads file via http and runs it through
    processor function for extraction"""
    result = None
    logging.debug('[get_data] Starting the download of %s', tar_url)
    req = requests.get(tar_url, stream=True, allow_redirects=True)
    with NamedTemporaryFile() as buf:
        for block in req.iter_content(chunk_size=4096):
            buf.write(block)
        buf.flush()
        logging.debug('[get_data] Download finished, starting extraction')
        result = processor(buf, target)

    logging.debug('[get_data] File extracted to %s', result.as_posix())
    return result.as_posix()
