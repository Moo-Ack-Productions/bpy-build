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


class TestBpyBuild(unittest.TestCase):
    """A lot of the argument stuff requires complex
    unittest mocking, half of which I only learned from
    a few StackOverflow posts. I am not liable for whatever
    chaos this may cause.

    Don't touch, it works.
    """

    @mock.patch("sys.stdout", new_callable=StringIO)
    def test_args(self, mock_stderr: StringIO) -> None:
        """Test arguments in BpyBuild."""
        with mock.patch("sys.argv", ["bab", "-h"]):
            with self.assertRaises(SystemExit):
                # Calling BpyBuild directly from
                # the main function rather then
                # launching a subprocess.
                bab.main()
        self.assertRegex(mock_stderr.getvalue(), r"usage: ")


if __name__ == "__main__":
    _ = unittest.main()
