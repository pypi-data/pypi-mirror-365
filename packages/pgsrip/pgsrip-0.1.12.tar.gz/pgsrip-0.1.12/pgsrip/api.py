import logging
import typing

from pgsrip import core
from pgsrip.media import Media, Pgs
from pgsrip.options import Options


logger = logging.getLogger(__name__)


def scan_path(path: str, options: typing.Optional[Options] = None):
    collected: typing.List[Media] = []
    filtered_out: typing.List[str] = []
    discarded: typing.List[str] = []
    core.scan_path(path, collected, filtered_out, discarded, options=options or Options())

    return collected, filtered_out, discarded


def rip(media: Media, options: typing.Optional[Options] = None):
    return core.rip(media, options or Options())


def rip_pgs(pgs: Pgs, options: typing.Optional[Options] = None):
    return core.rip_pgs(pgs, options or Options())
