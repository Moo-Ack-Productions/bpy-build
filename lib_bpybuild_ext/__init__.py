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

# This is a reimplementation of the Blender Extension builder due to licensing
# restrictions. BpyBuild is under the BSD 3-Clause license, whereas the Blender
# Extension builder is under the GPL-2.0-or-later license. Thus, we simply can't
# use the Blender implementation in BpyBuild.
#
# Some might call us evil for this, but it's simply impractical for us to relicense
# a BSD 3-Clause licensed program under the GPL, especially one with an API.
#
# This reimplementation will be independent from the rest of BpyBuild so that developers
# can create tools around Blender Extensions with a library that is under a more permissive
# license.
#
# Unlike the rest of BpyBuild, where exceptions aren't really used, this library will
# use exceptions since that's common in the Python world. All functions that can raise an
# exception explicitly will say what they can raise in their documentation.
#
# Due to the complexity of the Blender Extension builder, which is a 4000 line long script
# containing code for everything extension related from extension building to the extesion
# repo, this is based exclusively on information in the Blender manual. If it's not important
# enough to include in the manual, then it isn't important enough to be in a third-party
# reimplementation of the extension builder.

from __future__ import annotations

import re
from pathlib import Path
from typing import cast

import tomli

from . import manifest

BLENDER_MANIFEST = "blender_manifest.toml"

BLACKLISTED_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f-\x9f]")


def validate_string_safety(value: str) -> bool:
    """Validate a string value. This exists in order to make
    sure strings don't contain control characters that could be used
    for malicious purposes.

    Although not documented, this is important for security reasons.

    :param value: The string to check
    :type value: str

    :return: Boolean representing if the string is secure
    :rtype: bool
    """
    for _ in BLACKLISTED_CONTROL_CHARS.finditer(value):
        return False
    return True


def get_manifest_data(manifest_path: Path) -> manifest.ManifestData:
    """Read blender_manifest.toml and parse it into an object representing the manifest data.

    :param manifest_path: The path to blender_manifest.toml
    :type manifest_path: Path

    :return: Python object representing the manifest data
    :rtype: ManifestData optional

    :raises FileNotFoundError: If manifest_path is not found
    :raises tomli.TOMLDecodeError: If blender_manifest.toml is invalid
    :raises TypeError: If a manifest value in blender_manifest.toml is not the correct type or value
    """

    if not manifest_path.exists():
        raise FileNotFoundError(f"{manifest_path} does not exist!")

    with open(manifest_path, "rb") as mf:
        raw_manifest_data: manifest.ManifestTypedDict = cast(
            manifest.ManifestTypedDict, tomli.load(mf)
        )

    manifest_data = manifest.ManifestData()

    # Iterate over all of the items in the manifest.
    #
    # In order to simply this entire loop, we take
    # advantage of hasattr, getattr, and setattr, which
    # allow us to dynamically check, get, and set an attr
    # on manifest_data based on the string keys in raw_manifest_data.
    for key, val in raw_manifest_data.items():
        if isinstance(val, str):
            if not validate_string_safety(val):
                raise TypeError(
                    f"{key} contains value that uses blacklisted characters"
                )
        if hasattr(manifest_data, key):
            # TODO: Enable when we move to Python 3.9
            # if not isinstance(val, manifest.ManifestData.__annotations__[key]):  # type: ignore[misc]
            #    # TODO: Implement a way to tell the user what type it should be
            #    raise TypeError(
            #        f"{key} is not the correct type! See the Blender docs for more info"
            #    )
            setattr(manifest_data, key, val)  # type: ignore[misc]
    return manifest_data
