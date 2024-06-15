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

from __future__ import annotations

from pathlib import Path
from typing import cast

import tomli

from . import manifest

BLENDER_MANIFEST = "blender_manifest.toml"


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
        if hasattr(manifest_data, key):
            if not isinstance(val, getattr(manifest_data, key)):  # type: ignore[misc]
                # TODO: Implement a way to tell the user what type it should be
                raise TypeError(
                    f"{key} is not the correct type! See the Blender docs for more info"
                )
            setattr(manifest_data, key, val)  # type: ignore[misc]
    return manifest_data


def build_ext(ext_path: Path, output_path: Path) -> None:
    """Build an extension

    This takes the extension located at ext_path and builds
    the extension in output_path.

    :param ext_path: The folder where the extension is stored
    :type ext_path: Path

    :param output_path: The folder where the final build should be outputted
    :type output_path: Path

    :raises NotADirectoryError: If ext_path or output_path is not a directory
    :raises FileExistsError: If ext_path and output_path are the same
    :raises FileNotFoundError: If ext_path, output_path, or  ext_path/blender_manifest.toml are not found
    """

    if not ext_path.exists():
        raise FileNotFoundError("Extension path doesn't exist!")

    if not ext_path.is_dir():
        raise NotADirectoryError(f"Extension path must a directory, got {ext_path}")

    if not output_path.exists():
        raise FileNotFoundError("Output path doesn't exist!")

    if not output_path.is_dir():
        raise NotADirectoryError(f"Output path must be a directory, got {output_path}")

    if ext_path == output_path:
        raise FileExistsError("Extension path and output path are the same!")

    manifest_path = Path(ext_path, BLENDER_MANIFEST)
    if not manifest_path.exists():
        raise FileNotFoundError(f"Can not find {manifest_path}")
    _manifest_data = get_manifest_data(manifest_path)
