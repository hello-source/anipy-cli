import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import Union, Optional

from anipy_cli.version import __version__

@dataclass(frozen=True)
class CliArgs:
    download: bool
    binge: bool
    history: bool
    seasonal: bool
    mal: bool
    delete: bool
    quality: Optional[Union[str, int]]
    ffmpeg: bool
    no_season_search: bool
    auto_update: bool
    optional_player: Optional[str]
    location: Optional[Path]
    mal_password: Optional[str]
    config: bool


def parse_args(args: list[str] = None) -> CliArgs:
    parser = argparse.ArgumentParser(
        description="Play Animes from gogoanime in local video-player or Download them.",
        add_help=False,
    )

    # Workaround, so the Mutally Exclusive group can have a custom title+description
    actions_group = parser.add_argument_group(
        "Actions", "Different Actions and Modes of anipy-cli (only pick one)"
    )
    actions_group = actions_group.add_mutually_exclusive_group()

    options_group = parser.add_argument_group(
        "Options", "Options to change the behaviour of anipy-cli"
    )
    info_group = parser.add_argument_group(
        "Info", "Info about the current anipy-cli installation"
    )

    actions_group.add_argument(
        "-D",
        "--download",
        required=False,
        dest="download",
        action="store_true",
        help="Download mode. Download multiple episodes like so: first_number-second_number (e.g. 1-3)",
    )

    actions_group.add_argument(
        "-B",
        "--binge",
        required=False,
        dest="binge",
        action="store_true",
        help="Binge mode. Binge multiple episodes like so: first_number-second_number (e.g. 1-3)",
    )

    actions_group.add_argument(
        "-H",
        "--history",
        required=False,
        dest="history",
        action="store_true",
        help="Show your history of watched anime",
    )

    actions_group.add_argument(
        "-S",
        "--seasonal",
        required=False,
        dest="seasonal",
        action="store_true",
        help="Seasonal Anime mode. Bulk download or binge watch newest episodes.",
    )

    actions_group.add_argument(
        "-M",
        "--my-anime-list",
        required=False,
        dest="mal",
        action="store_true",
        help="MyAnimeList mode. Similar to seasonal mode, but using MyAnimeList "
        "(requires MAL account credentials to be set in config).",
    )

    actions_group.add_argument(
        "--delete-history",
        required=False,
        dest="delete",
        action="store_true",
        help="Delete your History.",
    )

    options_group.add_argument(
        "-q",
        "--quality",
        action="store",
        required=False,
        default="best",
        type=lambda v: int(v) if v.isdigit() else v,
        help="Change the quality of the video, accepts: best, worst or 360, 480, 720 etc.  Default: best",
    )

    options_group.add_argument(
        "-f",
        "--ffmpeg",
        required=False,
        dest="ffmpeg",
        action="store_true",
        help="Use ffmpeg to download m3u8 playlists, may be more stable but is way slower than internal downloader",
    )

    options_group.add_argument(
        "-o",
        "--no-seas-search",
        required=False,
        dest="no_season_search",
        action="store_true",
        help="Turn off search in season. "
        "Disables prompting if GoGoAnime is to be searched for anime in specific season.",
    )

    options_group.add_argument(
        "-a",
        "--auto-update",
        required=False,
        dest="auto_update",
        action="store_true",
        help="Automatically update and download all Anime in seasonals list from start EP to newest.",
    )

    options_group.add_argument(
        "-p",
        "--optional-player",
        required=False,
        choices=["mpv", "vlc", "syncplay", "mpvnet"],
        help="Override the player set in the config.",
    )

    options_group.add_argument(
        "-l",
        "--location",
        required=False,
        dest="location",
        action="store",
        type=Path,
        default=None,
        help="Override all configured download locations",
    )

    options_group.add_argument(
        "--mal-password",
        required=False,
        dest="mal_password",
        action="store",
        help="Provide password for MAL login (overrides password set in config)",
    )

    info_group.add_argument(
        "-h", "--help", action="help", help="show this help message and exit"
    )

    info_group.add_argument("-v", "--version", action="version", version=__version__)

    info_group.add_argument(
        "--config-path",
        required=False,
        dest="config",
        action="store_true",
        help="Print path to the config file.",
    )

    return CliArgs(**vars(parser.parse_args(args=args)))
