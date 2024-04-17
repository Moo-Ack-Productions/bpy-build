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

import unittest
from unittest import mock
from io import StringIO
import bpy_addon_build as bab
from bpy_addon_build.build_context.install import get_paths
from pathlib import Path

# parent folder of the tests
TEST_FOLDER = Path(__file__).parent
VERSIONS = [2.8, 3.4, 3.5]


class TestBpyBuild(unittest.TestCase):
    """A lot of the argument stuff requires complex
    unittest mocking, half of which I only learned from
    a few StackOverflow posts. I am not liable for whatever
    chaos this may cause.

    Don't touch, it works.
    """

    @mock.patch("sys.stdout", new_callable=StringIO)
    def test_args(self, mock_stdout: StringIO) -> None:
        """Test arguments in BpyBuild.

        This runs the help command for BpyBuild and checks
        to see if the help message is printed.
        """
        with mock.patch("sys.argv", ["bab", "-h"]):
            with self.assertRaises(SystemExit):
                # Calling BpyBuild directly from
                # the main function rather then
                # launching a subprocess.
                bab.main()
        self.assertRegex(mock_stdout.getvalue(), r"usage: ")

    @mock.patch("sys.stdout", new_callable=StringIO)
    def test_non_existant(self, _: StringIO) -> None:
        """Test if BpyBuild returns an exception
        when a non-existant config file is passed.

        This runs BpyBuild with -c doesnt_exist and check
        if a FileNotFoundError is raised with the message
        "File doesnt_exist does not exist!"
        """
        with mock.patch("sys.argv", ["bab", "-c", "doesnt_exist"]):
            with self.assertRaises(FileNotFoundError) as cm:
                bab.main()
        self.assertEqual(str(cm.exception), "File doesnt_exist does not exist!")

    @mock.patch("sys.stdout", new_callable=StringIO)
    def test_build(self, mock_stdout: StringIO) -> None:
        """Perform a test build using the
        project in test_addon.

        For our test addon, this will perform a build
        without any actions, and will check for the
        following:
        - Build folder
        - MCprep_addon.zip
        - stage-1 folder
        - "MAIN" in mock_stdout
        """
        with mock.patch(
            "sys.argv", ["bab", "-c", f"{TEST_FOLDER}/test_addon/bpy-build.yaml"]
        ):
            bab.main()
        build = Path(f"{TEST_FOLDER}/test_addon/build")
        self.assertTrue(build.exists() and build.is_dir())
        self.assertTrue((build / "MCprep_addon.zip").exists())
        self.assertTrue((build / "stage-1").exists())

        # Check mock_stdout for expected strings.
        self.assertRegex(mock_stdout.getvalue(), r"MAIN")  # default action

    @mock.patch("sys.stdout", new_callable=StringIO)
    def test_actions(self, mock_stdout: StringIO) -> None:
        """Perform a test build using the
        project in test_addon

        This is identical to test_build, but
        the build command is now ran with -b dev,
        which adds some extra things to check for.

        This test will check for:
        - Build folder
        - MCprep_addon.zip
        - stage-1 folder
        - stage-1/MCprep_addon/mcprep_dev.txt
        - Lack of stage-1/MCprep_addon/ignore.blend
        - "DEV MAIN" in mock_stdout
        - "MAIN" in mock_stdout
        - "hi guys c:" in stage-1/MCprep_addon/mcprep_dev.txt
        """
        with mock.patch(
            "sys.argv",
            ["bab", "-c", f"{TEST_FOLDER}/test_addon/bpy-build.yaml", "-b", "dev"],
        ):
            bab.main()
        build = Path(f"{TEST_FOLDER}/test_addon/build")

        # This could be consolidated into a single call,
        # but I feel this is more readable as it's calling
        # for each individual condition, and reduces complexity.
        self.assertTrue(build.exists() and build.is_dir())
        self.assertTrue((build / "MCprep_addon.zip").exists())
        self.assertTrue((build / "stage-1").exists())
        self.assertTrue((build / "stage-1/MCprep_addon/mcprep_dev.txt").exists())
        self.assertFalse((build / "stage-1/MCprep_addon/ignore.blend").exists())

        # Check mock_stdout and mcprep_dev.txt for some
        # expected strings.
        self.assertRegex(mock_stdout.getvalue(), r"DEV MAIN")  # dev action
        self.assertRegex(mock_stdout.getvalue(), r"MAIN")  # default action

        with open(build / "stage-1/MCprep_addon/mcprep_dev.txt", "r") as f:
            self.assertEqual(f.read().strip(), "hi guys c:")

    @mock.patch("sys.stdout", new_callable=StringIO)
    def test_hooks(self, mock_stdout: StringIO) -> None:
        """Perform a test build using the
        project in test_addon.

        This uses the standard default action, but
        now checks for the output of different
        hooks in mock_stdout.

        To make sure this test is accurate, we
        use the -s flag to suppress extra BpyBuild
        output.

        This test will check for:
        - "PRE BUILD {TEST_FOLDER}/test/test_addon/MCprep_addon" in mock_stdout
        - "MAIN {TEST_FOLDER}/test/test_addon/build/stage-1/MCprep_addon" in mock_stdout
        - "POST INSTALL {install_path}" in mock_stdout
        - "CLEAN UP {TEST_FOLDER}/test/test_addon/MCprep_addon" in mock_stdout

        TODO: add more complexity to hooks
        """
        with mock.patch(
            "sys.argv",
            ["bab", "-c", f"{TEST_FOLDER}/test_addon/bpy-build.yaml", "-s"],
        ):
            bab.main()

        # Check mock_stdout for expected strings.
        stdout_list = mock_stdout.getvalue().split("\n")
        self.assertIn(f"PRE BUILD {TEST_FOLDER}/test_addon/MCprep_addon", stdout_list)
        self.assertIn(
            f"MAIN {TEST_FOLDER}/test_addon/build/stage-1/MCprep_addon", stdout_list
        )
        self.assertIn(f"CLEAN UP {TEST_FOLDER}/test_addon/MCprep_addon", stdout_list)

        # Check the post install paths. This can be
        # different depending on the system and the
        # versions of Blender intsalled.
        for path in get_paths(VERSIONS):
            self.assertIn(f"POST INSTALL {path}", stdout_list)

    @mock.patch("sys.stdout", new_callable=StringIO)
    def test_old(self, mock_stdout: StringIO) -> None:
        """Performs a test build using the
        project in test_addon.

        This will test backwards compatibility
        with the old main function type, with the
        "old" action.

        This test will check for:
        - "OLD MAIN" in mock_stdout
        - mcprep_dev.txt in stage-1/MCprep_addon
        - "hi guys c:" in mcprep_dev.txt
        """
        with mock.patch(
            "sys.argv",
            ["bab", "-c", f"{TEST_FOLDER}/test_addon/bpy-build.yaml", "-b", "old"],
        ):
            bab.main()

        # Check mock_stdout for expected string.
        self.assertRegex(mock_stdout.getvalue(), r"OLD MAIN")
        self.assertTrue(
            (
                Path(
                    f"{TEST_FOLDER}/test_addon/build/stage-1/MCprep_addon/mcprep_dev.txt"
                )
            ).exists()
        )
        self.assertEqual(
            (
                Path(
                    f"{TEST_FOLDER}/test_addon/build/stage-1/MCprep_addon/mcprep_dev.txt"
                )
            )
            .read_text()
            .strip(),
            "hi guys c:",
        )


if __name__ == "__main__":
    _ = unittest.main()
