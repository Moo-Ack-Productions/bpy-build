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

# This is a test using the MCprep addon, which uses BpyBuild in production.
#
# This won't test every feature of BpyBuild (unlike tests.py), but the tests
# are far more sophisticated due to added complexity.

import unittest
from unittest import mock
from io import StringIO
import bpy_addon_build as bab
from bpy_addon_build.build_context.install import get_paths
from pathlib import Path
from git import Repo
import shutil
import urllib.request
import hashlib
import sys

# parent folder of the tests
TEST_FOLDER = Path(__file__).parent
VERSIONS = [2.8, 3.4, 3.5]
MCPREP_REPO = f"{TEST_FOLDER}/MCprep"

# The commit to clone from
MCPREP_SHA = "a95b7e9fb3ac229562897892a8f811bcedafe468"
MCPREP_URL = "https://github.com/Moo-Ack-Productions/MCprep.git"

POLIB_SHA = "cc05cfd048cb85031b51aef8c5c720fa9930624b"
POLIB_URL = f"https://raw.githubusercontent.com/izimobil/polib/{POLIB_SHA}/polib.py"
POLIB_HASH = "3a4dc3d0682cf71f9bbfc40e526b58e4beaa6171a49712f6182736a45b797e9a"


class TestBpyBuildProd(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """Clone the MCprep repo, download
        polib to deps/, verify the sha256 checksum,
        and add deps/ to sys.path.
        """
        repo = Repo.clone_from(MCPREP_URL, MCPREP_REPO, branch="milestone-3-6-0")  # type: ignore
        repo.commit(MCPREP_SHA)
        _ = urllib.request.urlretrieve(POLIB_URL, f"{TEST_FOLDER}/deps/polib.py")
        with open(f"{TEST_FOLDER}/deps/polib.py", "rb") as file:
            polib = file.read()
        hasher = hashlib.sha256()
        hasher.update(polib)
        assert hasher.hexdigest() == POLIB_HASH
        sys.path.append(f"{TEST_FOLDER}/deps")

    @classmethod
    def tearDownClass(cls) -> None:
        """Remove the MCprep repo"""
        shutil.rmtree(f"{TEST_FOLDER}/MCprep")

    def test_config(self) -> None:
        """Check the MCprep repo if
        bpy-build.yaml exists"""
        self.assertTrue(Path(f"{MCPREP_REPO}/bpy-build.yaml").exists())

    @mock.patch("sys.stdout", new_callable=StringIO)
    def test_build(self, mock_stdout: StringIO) -> None:
        """Perform a test build of MCprep at the path
        defined in MCPREP_REPO.

        The following tests are performed:
        - stage-1 in build/
        - MCprep_addon.zip in build/
        - MCprep installed in the right paths
        """

        with mock.patch("sys.argv", ["bab", "-c", f"{MCPREP_REPO}/bpy-build.yaml"]):
            bab.main()

        # Check if the build/ folder exists
        self.assertTrue(Path(f"{MCPREP_REPO}/build").exists())

        # Check if the MCprep_addon.zip exists
        self.assertTrue(Path(f"{MCPREP_REPO}/build/MCprep_addon.zip").exists())

        # Check if the MCprep addon is installed in the right paths
        for version in get_paths(VERSIONS):
            self.assertTrue(Path(f"{version}/MCprep_addon").exists())


if __name__ == "__main__":
    _ = unittest.main()
