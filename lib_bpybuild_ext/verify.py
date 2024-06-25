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

from typing import cast, get_args

from . import manifest

COMPATIBLE_SCHEMA_VERSIONS = ["1.0.0"]

# TODO: Implement theme support
EXTENSION_TYPES = ["add-on"]


def verify_manifest(manifest_data: manifest.ManifestData) -> None:
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

    :param manifest: The manifest data parsed from blender_manifest.toml
    :type manifest: ManifestData

    :raises TypeError: If a manifest value does not pass manifest verification
    """

    if manifest_data.schema_version not in COMPATIBLE_SCHEMA_VERSIONS:
        raise TypeError("Schema version incompatible with LibBpyBuildExt")

    # Although the Blender Extension builder allows ), }, and ] at the
    # the end of taglines, we will simply not support it as this is not
    # not mention in the documentation. If it isn't important enough to be
    # mentioned in the documentation, it isn't needed in LibBpyBuildExt
    if not manifest_data.tagline[-1:].isalnum():
        raise TypeError("Tagline must not end in punctuation")

    for license in manifest_data.license:
        if license[:4] != "SPDX":
            raise TypeError(f'License {license} missing "SPDX:" prefix')

    if manifest_data.type not in EXTENSION_TYPES:
        raise TypeError(f"Invalid extension type; supported types: {EXTENSION_TYPES}")

    if manifest_data.tags is not None:
        for t in manifest_data.tags:
            if t not in cast(tuple[str], get_args(manifest.ManifestTagsLiteral)):
                raise TypeError(
                    f"{t} is not a compatible tag; supported tags: {cast(tuple[str], get_args(manifest.ManifestTagsLiteral))}"
                )

    if manifest_data.permissions is not None:
        for p in manifest_data.permissions:
            if p not in cast(tuple[str], get_args(manifest.ManifestPermissionsLiteral)):
                raise TypeError(
                    f"{p} is not a valid permission; supported permissions {manifest.ManifestPermissionsLiteral}"
                )
            if not manifest_data.permissions[
                cast(manifest.ManifestPermissionsLiteral, p)
            ][-1:].isalnum():
                raise TypeError(
                    f"Explaination for permission {p} must not end in punctuation"
                )
