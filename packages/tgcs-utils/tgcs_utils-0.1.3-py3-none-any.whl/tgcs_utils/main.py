from __future__ import annotations

from cappa import Subcommands, command, invoke
from dataclasses import dataclass

from .create_build_env import TGCSCreateBuildEnv
from .extract_version import TGCSExtractVersion
from .release import TGCSRelease


@command(name="tgcs-utils")
@dataclass
class TGCSUtils:
    subcommand: Subcommands[TGCSCreateBuildEnv | TGCSExtractVersion | TGCSRelease]


def main():
    invoke(TGCSUtils)


if __name__ == "__main__":
    main()
