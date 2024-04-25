from dataclasses import dataclass, field
from pathlib import Path
from time import time
from typing import TYPE_CHECKING, Dict, Optional

from dataclasses_json import DataClassJsonMixin, config

from anipy_api.provider import Episode

if TYPE_CHECKING:
    from anipy_api.anime import Anime


@dataclass
class HistoryEntry(DataClassJsonMixin):
    provider: str = field(metadata=config(field_name="pv"))
    identifier: str = field(metadata=config(field_name="id"))
    name: str = field(metadata=config(field_name="na"))
    episode: Episode = field(metadata=config(field_name="ep"))
    timestamp: int = field(metadata=config(field_name="ts"))
    dub: bool = field(metadata=config(field_name="d"))
    has_dub: bool = field(metadata=config(field_name="hd"))

    def __repr__(self) -> str:
        return f"{self.name} ({'dub' if self.dub else 'sub'}) Episode {self.episode}"

    def __hash__(self) -> int:
        return hash(f"{self.provider}:{'dub' if self.dub else 'sub'}:{self.identifier}")


@dataclass
class History(DataClassJsonMixin):
    history: Dict[str, HistoryEntry]

    def write(self, file: Path):
        file.write_text(self.to_json())

    @staticmethod
    def read(file: Path) -> "History":
        if not file.is_file():
            file.parent.mkdir(exist_ok=True, parents=True)
            return History({})

        try:
            history: History = History.from_json(file.read_text())
        except KeyError:
            history = _migrate_history(file)

        return history


def get_history(file: Path) -> History:
    return History.read(file)


def get_history_entry(file: Path, anime: "Anime", dub: bool) -> Optional[HistoryEntry]:
    history = History.read(file)
    uniqueid = _get_uid(anime, dub)

    return history.history.get(uniqueid, None)


def update_history(file: Path, anime: "Anime", episode: "Episode", dub: bool):
    history = History.read(file)

    uniqueid = _get_uid(anime, dub)
    entry = history.history.get(uniqueid, None)

    if entry is None:
        entry = HistoryEntry(
            provider=anime.provider.NAME,
            identifier=anime.identifier,
            name=anime.name,
            episode=episode,
            timestamp=int(time()),
            has_dub=anime.has_dub,
            dub=dub,
        )
    else:
        entry.episode = episode
        entry.timestamp = int(time())

    history.history[uniqueid] = entry

    history.write(file)


def _get_uid(anime: "Anime", dub: bool):
    return f"{anime.provider.NAME}:{'dub' if dub else 'sub'}:{anime.identifier}"


def _migrate_history(file):
    import json
    import re

    old_data = json.load(file.open("r"))
    new_history = History({})

    for k, v in old_data.items():
        name = k
        name = re.sub(r"\s?\((dub|japanese\sdub)\)", "", name, flags=re.IGNORECASE)
        identifier = Path(v["category-link"]).name
        is_dub = identifier.endswith("-dub") or identifier.endswith("-japanese-dub")
        identifier = identifier.removesuffix("-dub").removesuffix("-japanese-dub")

        episode = v["ep"]
        timestamp = int(time())
        unique_id = f"gogoanime:{'dub' if is_dub else 'sub'}:{identifier}"
        new_entry = HistoryEntry(
            provider="gogoanmie",
            name=name,
            identifier=identifier,
            episode=episode,
            timestamp=timestamp,
            has_dub=is_dub,
            dub=is_dub,
        )

        new_history.history[unique_id] = new_entry

    new_history.write(file)
    return new_history
