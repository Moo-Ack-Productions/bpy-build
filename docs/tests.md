# Using BpyBuild in Unittests
Some addons have tests that they perform to make sure the addon works across multiple versions of Blender. Often, these tests require fresh building with BpyBuild. Although BpyBuild could be ran as a subprocess, this isn't recommended. 

The recommended way of running BpyBuild through tests is using Python's `unittest` module, taking advantage of mocking features. This is how we call BpyBuild in tests when we need to test a new feature. 

For example:
```py
import unittest
from unittest import mock
from io import StringIO
import bpy_addon_build as bab
from pathlib import Path

class TestBpyBuild(unittest.TestCase):
    def test_addon(self, mock_stdout: StringIO) -> None:
        with mock.patch("sys.argv", ["bab", "rest", "of" "the" "arguments"]):
            bab.main()
```

This calls BpyBuild's `main` function directly, and with mocking, we can pass the arguments we want, without having to modify `sys.argv` itself.

If you need to validate if the addon was installed properly, that can also be done:
```py
from bpy_addon_build.build_context.install import get_paths
VERSIONS = [2.8, 3.0, ...]

# ...

for path in get_paths(VERSIONS):
    # ...
```
