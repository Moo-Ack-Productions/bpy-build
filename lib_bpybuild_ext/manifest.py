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

from dataclasses import dataclass, field
from typing import Literal, Optional

from typing_extensions import NotRequired, TypedDict

# Note: We only support the addon subset of manifest data, and
# only 1.0.0 of the manifest schema
#
# TODO: Implement theme support
ManifestSchemaLiteral = Literal["1.0.0"]
ManifestTypeLiteral = Literal["add-on"]
ManifestTagsLiteral = Literal[
    "3D View",
    "Add Curve",
    "Add Mesh",
    "Animation",
    "Bake",
    "Camera",
    "Compositing",
    "Development",
    "Game Engine",
    "Geometry Nodes",
    "Grease Pencil",
    "Import-Export",
    "Lighting",
    "Material",
    "Modeling",
    "Mesh",
    "Node",
    "Object",
    "Paint",
    "Pipeline",
    "Physics",
    "Render",
    "Rigging",
    "Scene",
    "Sculpt",
    "Sequencer",
    "System",
    "Text Editor",
    "Tracking",
    "User Interface",
    "UV",
]

ManifestPlatformLiteral = Literal[
    "windows-amd64", "macos-arm64", "linux-x86_64", "windows-arm64", "macos-x86_64"
]

ManifestPermissionsLiteral = Literal[
    "files", "network", "clipboard", "camera", "microphone"
]


class ManifestBuildTypedDict(TypedDict):
    paths_exclude_pattern: NotRequired[list[str]]


class ManifestPermissionsTypedDict(TypedDict):
    files: NotRequired[str]
    network: NotRequired[str]
    clipboard: NotRequired[str]
    camera: NotRequired[str]
    microphone: NotRequired[str]


class ManifestTypedDict(TypedDict):
    schema_version: ManifestSchemaLiteral
    id: str
    version: str
    name: str
    tagline: str
    maintainer: str
    type: ManifestTypeLiteral

    permissions: NotRequired[ManifestPermissionsTypedDict]
    website: NotRequired[str]
    tags: NotRequired[list[ManifestTagsLiteral]]

    blender_version_min: str
    blender_version_max: NotRequired[str]

    license: list[str]
    copyright: NotRequired[list[str]]

    platforms: NotRequired[list[ManifestPlatformLiteral]]
    wheels: NotRequired[list[str]]
    build: NotRequired[ManifestBuildTypedDict]


@dataclass
class ManifestData:
    schema_version: ManifestSchemaLiteral = "1.0.0"
    id: str = "my_example_extension"
    version: str = "1.0.0"
    name: str = "Test Extension"
    tagline: str = "This is another extension"
    maintainer: str = "Developer name <email@address.com>"
    type: ManifestTypeLiteral = "add-on"

    permissions: Optional[ManifestPermissionsTypedDict] = None
    website: Optional[str] = None
    tags: Optional[list[ManifestTagsLiteral]] = None

    blender_version_min: str = "4.2.0"
    blender_version_max: Optional[str] = None

    license: list[str] = field(default_factory=lambda: ["SPDX:GPL-2.0-or-later"])
    copyright: Optional[list[str]] = None

    platforms: Optional[list[ManifestPlatformLiteral]] = None
    wheels: Optional[list[str]] = None
    build: Optional[ManifestBuildTypedDict] = None
