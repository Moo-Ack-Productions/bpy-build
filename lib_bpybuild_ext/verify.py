# BSD 3-Clause License
#
# Copyright (c) 2024, Mahid Sheikh
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Disclaimer: This is not a product from VLK Architects or VLK Experience Design,
# nor is this endorsed by VLK Architects or VLK Experience Design

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import cast, get_args

from packaging.version import InvalidVersion, Version

from . import manifest

RE_MANIFEST_SEMVER = re.compile(
    r"^"
    r"(?P<major>0|[1-9]\d*)\."
    r"(?P<minor>0|[1-9]\d*)\."
    r"(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)

CHARACTER_LIMIT = 64


def verify_manifest(manifest_data: manifest.ManifestData, manifest_path: Path) -> None:
    """Verify a Blender Extension manifest based on the
    criteria given by the Blender manual.

    We are aware that there is some extra things that the
    Blender Extension builder checks for upstream, but
    the way we see it, it's up to the Blender Foundation
    to properly document everything. If it isn't important
    enough for them to document it, then it isn't important
    enough for us to implement it.

    We don't check for missing values because we already assign a
    set of default values anyway.

    :param manifest_data: The manifest data parsed from blender_manifest.toml
    :type manifest_data: ManifestData

    :param manifest_path: the path to the manifest
    :type manifest_path: Path

    :raises TypeError: If a manifest value does not pass manifest verification
    """

    # TODO: Sort this better

    # If it's not in our list of compatible schema versions, we
    # certainly can't parse or deal with it

    # Python 3.8 typing woes requires us to ignore these get_args calls
    if manifest_data.schema_version not in get_args(manifest.ManifestSchemaLiteral):  # type: ignore[misc]
        raise TypeError("Schema version incompatible with LibBpyBuildExt")

    if not RE_MANIFEST_SEMVER.match(manifest_data.version):
        raise TypeError("Version must be in semantic versioning format")

    try:
        min_version = Version(manifest_data.blender_version_min)
        v4_2 = Version("4.2.0")
        if min_version < v4_2:
            raise TypeError(
                "Extensions are not supported in versions of Blender prior to 4.2"
            )
    except InvalidVersion:
        raise TypeError(
            f"{manifest_data.blender_version_min} is not in the correct format that Blender versions follow"
        )

    if manifest_data.blender_version_max is not None:
        try:
            min_version = Version(manifest_data.blender_version_min)
            max_version = Version(manifest_data.blender_version_max)
            if min_version == max_version:
                raise TypeError(
                    "Cannot use the same version for both blender_version_min and blender_version_max"
                )
        except InvalidVersion:
            raise TypeError(
                f"{manifest_data.blender_version_max} is not in the correct format that Blender versions follow"
            )

    # Although the Blender Extension builder allows ), }, and ] at the
    # the end of taglines, we will simply not support it as this is not
    # not mention in the documentation. If it isn't important enough to be
    # mentioned in the documentation, it isn't needed in LibBpyBuildExt
    if not manifest_data.tagline[-1:].isalnum():
        raise TypeError("Tagline must not end in punctuation")

    if len(manifest_data.tagline) == CHARACTER_LIMIT:
        raise TypeError("Tagline can not be greater then 64 characters!")

    # TODO: Check against the SPDX database to validate
    # that the passed license is indeed a SPDX license
    for license in manifest_data.license:
        if license[:4] != "SPDX":
            raise TypeError(f'License {license} missing "SPDX:" prefix')

    # Python 3.8 typing woes requires us to ignore these get_args calls
    if manifest_data.type not in get_args(manifest.ManifestTypeLiteral):  # type: ignore[misc]
        raise TypeError(
            f"Invalid extension type; supported types: {get_args(manifest.ManifestTypeLiteral)}"  # type: ignore[misc]
        )

    if manifest_data.tags is not None:
        for t in manifest_data.tags:
            # Python 3.8 typing woes requires us to ignore these get_args calls
            if t not in get_args(manifest.ManifestTagsLiteral):  # type: ignore[misc]
                raise TypeError(
                    f"{t} is not a compatible tag; supported tags: {cast(tuple[str], get_args(manifest.ManifestTagsLiteral))}"
                )

    if manifest_data.platforms is not None:
        for platform in manifest_data.platforms:
            if platform not in cast(
                tuple[str], get_args(manifest.ManifestPlatformLiteral)
            ):
                raise TypeError(
                    f"{platform} is not a supported platform; supported platforms: {cast(tuple[str], get_args(manifest.ManifestPlatformLiteral))}"
                )

    if manifest_data.copyright is not None:
        for copyright in manifest_data.copyright:
            year, _, name = copyright.partition(" ")
            if not all(x.isdigit() for x in year.partition("-")[0::2]):
                raise TypeError(
                    f'{copyright} is not in the proper format; supported format: ("YEAR First Last", "YEAR-YEAR First Last") '
                )
            if not name.strip():
                raise TypeError("Name for copyright must not be empty")

    if manifest_data.permissions is not None:
        for p in manifest_data.permissions:
            if p not in cast(tuple[str], get_args(manifest.ManifestPermissionsLiteral)):
                raise TypeError(
                    f"{p} is not a valid permission; supported permissions {manifest.ManifestPermissionsLiteral}"
                )

            # Not sure why, but Mypy requires we add
            # this explicit cast for p. Maybe because
            # TypedDict "only accepts" literals and we
            # have to tell it that p is a literal?
            if not manifest_data.permissions[
                cast(manifest.ManifestPermissionsLiteral, p)
            ][-1:].isalnum():
                raise TypeError(
                    f"Explaination for permission {p} must not end in punctuation"
                )

            if (
                len(
                    manifest_data.permissions[
                        cast(manifest.ManifestPermissionsLiteral, p)
                    ]
                )
                == CHARACTER_LIMIT
            ):
                raise TypeError(
                    f"Explaination for permission {p} may not be greater then 64 characters"
                )

    if manifest_data.wheels is not None:
        for wheel in manifest_data.wheels:
            if os.path.isabs(wheel):
                raise TypeError(
                    f"Wheel path {wheel} is absolute; paths must be relative"
                )
            if not Path(manifest_path.parent, wheel).exists():
                raise TypeError(f"Wheel path {wheel} does not exist!")
