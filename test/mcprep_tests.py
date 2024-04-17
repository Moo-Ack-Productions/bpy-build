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
#
# Git operations will have type checking ignored due to Mypy not being able
# to handle cls

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
import multiprocessing as mp
from multiprocessing.managers import DictProxy

# parent folder of the tests
TEST_FOLDER = Path(__file__).parent
VERSIONS = [2.8, 3.4, 3.5]
MCPREP_REPO = f"{TEST_FOLDER}/MCprep"

# The commit to clone from
MCPREP_SHA = "a95b7e9fb3ac229562897892a8f811bcedafe468"
MCPREP_URL = "https://github.com/Moo-Ack-Productions/MCprep.git"
MCPREP_BRANCH = "milestone-3-6-0"

POLIB_SHA = "cc05cfd048cb85031b51aef8c5c720fa9930624b"
POLIB_URL = f"https://raw.githubusercontent.com/izimobil/polib/{POLIB_SHA}/polib.py"
POLIB_HASH = "3a4dc3d0682cf71f9bbfc40e526b58e4beaa6171a49712f6182736a45b797e9a"


def clone_mcprep(repo: DictProxy) -> None:
    """Clone the MCprep repo"""
    print("Cloning MCprep...")
    repo["repo"] = Repo.clone_from(MCPREP_URL, MCPREP_REPO, branch=MCPREP_BRANCH)  # type: ignore
    repo["repo"].commit(MCPREP_SHA)  # type: ignore
    print("Cloned MCprep")


def download_polib() -> None:
    """Download polib to deps/"""
    print("Downloading polib...")
    _ = urllib.request.urlretrieve(POLIB_URL, f"{TEST_FOLDER}/deps/polib.py")
    print("Downloaded polib, verifying hash...")
    with open(f"{TEST_FOLDER}/deps/polib.py", "rb") as file:
        polib = file.read()
    hasher = hashlib.sha256()
    hasher.update(polib)
    assert hasher.hexdigest() == POLIB_HASH
    print("Verified polib")


class TestBpyBuildProd(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """Clone the MCprep repo, download
        polib to deps/, verify the sha256 checksum,
        and add deps/ to sys.path.
        """

        # This repo object allow
        # us to "return" the repo
        # object so we can set it
        # as a class attribute
        manager = mp.Manager()
        repo: DictProxy[str, Repo] = manager.dict()

        processes = [
            mp.Process(target=clone_mcprep, args=(repo,)),  # type: ignore
            mp.Process(target=download_polib),  # type: ignore
        ]
        for process in processes:
            process.start()

        for process in processes:
            process.join()

        # Add the repo object
        # to the class and set
        # sys.path to include deps/
        cls.repo = repo["repo"]  # type: ignore
        sys.path.append(f"{TEST_FOLDER}/deps")

    @classmethod
    def tearDownClass(cls) -> None:
        """Remove the MCprep repo"""
        shutil.rmtree(f"{TEST_FOLDER}/MCprep")
        Path(f"{TEST_FOLDER}/deps/polib.py").unlink()

    def test_config(self) -> None:
        """Check the MCprep repo if bpy-build.yaml exists"""
        self.assertTrue(Path(f"{MCPREP_REPO}/bpy-build.yaml").exists())

    @mock.patch("sys.stdout", new_callable=StringIO)
    def test_build(self, mock_stdout: StringIO) -> None:
        """Perform a test build of MCprep at the path defined in MCPREP_REPO.

        This test will check for:
        - stage-1 in build/
        - MCprep_addon.zip in build/
        - MCprep installed in the right paths
        """

        # Check if MCPREP_BRANCH is the current branch
        # and switch to it if not
        if TestBpyBuildProd.repo.active_branch.name != MCPREP_BRANCH:  # type: ignore
            TestBpyBuildProd.repo.git.checkout("-f", MCPREP_BRANCH)  # type: ignore

        with mock.patch("sys.argv", ["bab", "-c", f"{MCPREP_REPO}/bpy-build.yaml"]):
            bab.main()

        self.assertTrue(Path(f"{MCPREP_REPO}/build").exists())
        self.assertTrue(Path(f"{MCPREP_REPO}/build/MCprep_addon.zip").exists())

        # Check if the MCprep addon is installed in the right paths
        for version in get_paths(VERSIONS):
            self.assertTrue(Path(f"{version}/MCprep_addon").exists())

    @mock.patch("sys.stdout", new_callable=StringIO)
    def test_translations(self, mock_stdout: StringIO) -> None:
        """Perform a test build of MCprep at the path defined in
        MCPREP_REPO, but using the translate action by passing -b translate to bab.

        This test will check for:
        - stage-1 in build/
        - MCprep_addon.zip in build/
        - MCprep installed in the right paths
        - translations.py in stage-1/MCprep_addon
        - *.mo files in stage-1/MCprep_addon/MCprep_resources/Languages/
          where *.po files exist
        - "Building MO files..." in mock_stdout
        - "Building Translations..." in mock_stdout
        """

        # Check if MCPREP_BRANCH is the current branch
        # and switch to it if not
        if TestBpyBuildProd.repo.active_branch.name != MCPREP_BRANCH:  # type: ignore
            TestBpyBuildProd.repo.git.checkout("-f", MCPREP_BRANCH)  # type: ignore

        with mock.patch(
            "sys.argv",
            ["bab", "-c", f"{MCPREP_REPO}/bpy-build.yaml", "-b", "translate"],
        ):
            bab.main()

        self.assertTrue(Path(f"{MCPREP_REPO}/build").exists())
        self.assertTrue(Path(f"{MCPREP_REPO}/build/MCprep_addon.zip").exists())

        # Check if the MCprep addon is installed in the right paths
        for version in get_paths(VERSIONS):
            self.assertTrue(Path(f"{version}/MCprep_addon").exists())

        # Check if the translations are in the right paths
        self.assertTrue(
            Path(f"{MCPREP_REPO}/build/stage-1/MCprep_addon/translations.py").exists()
        )
        self.assertTrue(
            Path(
                f"{MCPREP_REPO}/build/stage-1/MCprep_addon/MCprep_resources/Languages/"
            ).exists()
        )

        path = Path(
            f"{MCPREP_REPO}/build/stage-1/MCprep_addon/MCprep_resources/Languages/"
        )
        for po in path.glob("*.po"):
            self.assertTrue(Path(f"{path}/{po.stem}.mo").exists())

        # Check mock_stdout for expected strings.
        stdout_list = mock_stdout.getvalue().split("\n")
        self.assertIn("Building MO files...", stdout_list)
        self.assertIn("Building Translations...", stdout_list)

    @mock.patch("sys.stdout", new_callable=StringIO)
    def test_hook_patch(self, mock_stdout: StringIO) -> None:
        """Perform a test build of MCprep at the path defined in MCPREP_REPO,
        but on the xgettext-replacement-action branch, patched with {TEST_FOLDER}/mcprep-patches/build_pot_prebuild.patch.

        This is to make sure hooks can be migrated easily
        with simple changes.

        This test will check for:
        - stage-1 in build/
        - MCprep_addon.zip in build/
        - MCprep installed in the right paths
        - mcprep.pot in MCPREP_REPO/MCprep_addon/MCprep_resources/Languages/
        """

        # Switch branch and patch
        TestBpyBuildProd.repo.git.checkout("-f", "xgettext-replacement-action")  # type: ignore
        TestBpyBuildProd.repo.git.apply(  # type: ignore
            f"{TEST_FOLDER}/mcprep-patches/build_pot_prebuild.patch"
        )

        with mock.patch(
            "sys.argv",
            [
                "bab",
                "-c",
                f"{MCPREP_REPO}/bpy-build.yaml",
                "-b",
                "xgettext-replacement-action",
            ],
        ):
            bab.main()

        self.assertTrue(Path(f"{MCPREP_REPO}/build").exists())
        self.assertTrue(Path(f"{MCPREP_REPO}/build/MCprep_addon.zip").exists())

        # Check if the MCprep addon is installed in the right paths
        for version in get_paths(VERSIONS):
            self.assertTrue(Path(f"{version}/MCprep_addon").exists())

        # Check if the mcprep.pot is in the right path
        self.assertTrue(
            Path(
                f"{MCPREP_REPO}/MCprep_addon/MCprep_resources/Languages/mcprep.pot"
            ).exists()
        )


if __name__ == "__main__":
    _ = unittest.main()
