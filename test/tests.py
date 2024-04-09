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
from pathlib import Path

# parent folder of the tests
TEST_FOLDER = Path(__file__).parent


class TestBpyBuild(unittest.TestCase):
    """A lot of the argument stuff requires complex
    unittest mocking, half of which I only learned from
    a few StackOverflow posts. I am not liable for whatever
    chaos this may cause.

    Don't touch, it works.
    """

    @mock.patch("sys.stdout", new_callable=StringIO)
    def test_args(self, mock_stdout: StringIO) -> None:
        """Test arguments in BpyBuild."""
        with mock.patch("sys.argv", ["bab", "-h"]):
            with self.assertRaises(SystemExit):
                # Calling BpyBuild directly from
                # the main function rather then
                # launching a subprocess.
                bab.main()
        self.assertRegex(mock_stdout.getvalue(), r"usage: ")

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
        """
        with mock.patch(
            "sys.argv", ["bab", "-c", f"{TEST_FOLDER}/test_addon/bpy-build.yaml"]
        ):
            bab.main()
        build = Path(f"{TEST_FOLDER}/test_addon/build")
        self.assertTrue(build.exists() and build.is_dir())
        self.assertTrue((build / "MCprep_addon.zip").exists())
        self.assertTrue((build / "stage-1").exists())

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
        """
        with mock.patch(
            "sys.argv",
            ["bab", "-c", f"{TEST_FOLDER}/test_addon/bpy-build.yaml", "-b", "dev"],
        ):
            bab.main()
        build = Path(f"{TEST_FOLDER}/test_addon/build")
        self.assertTrue(build.exists() and build.is_dir())
        self.assertTrue((build / "MCprep_addon.zip").exists())
        self.assertTrue((build / "stage-1").exists())
        self.assertTrue((build / "stage-1/MCprep_addon/mcprep_dev.txt").exists())


if __name__ == "__main__":
    _ = unittest.main()
