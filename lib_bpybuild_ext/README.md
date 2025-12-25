# LibBpyBuildExt

LibBpyBuildExt is a BSD 3-Clause reimplementation of the Blender Extension builder, with the
goal of creating an implementation of the Blender Extension builder under a more permissive
license, and as a library. This exists because the Blender Extension builder, while open source,
is under the GPL. Since BpyBuild is under the BSD 3-Clause license, a permissive reimplementation
is necessary.

Parity regarding manifest checks is based on the Blender documentation (with the exception of any
checks that exist for security reasons). Thus, in some ares, LibBpyBuildExt may be more permissive
than Blender itself, and in other areas, more strict than Blender itself. As long as the manifest
conforms to what is described in [the Blender manual](https://docs.blender.org/manual/en/latest/advanced/extensions/getting_started.html#manifest),
it will pass LibBpyBuildExt checks.

LibBpyBuildExt also adds the following checks:

- Use of `bl_info` after declaring it (`Error`)
    - Blender deletes `bl_info` in extensions, so references to `bl_info` will throw an exception
- Use of absolute imports (`Error`)
    - Absolute imports are not supported in extensions due to namespaces changes
- Themes with the Blender minimum not set to `5.0.0` (`Warning`)
    - Blender 5.0 filters out themes whose minimums are not set to `5.0.0`, due to breaking changes
    made to themes in Blender 5.0.

## Usage

```py
from pathlib import Path
from lib_bpybuild_ext import BLENDER_MANIFEST, compat, get_manifest_data, verify

# Retrieving manifest data and validating it
manifest_path = Path("path", "to", BLENDER_MANIFEST)
manifest_data = get_manifest_data(manifest_path) # Returns manifest data as a Python class
verify.verify_manifest(manifest_data, manifest_path) # Validates manifest values based on the Blender manual

# Checking addon source code for incompatibilities with extensions
# (intended for projects migrating from legacy addons to extensions)
addon_src_dir = Path("path", "to", "addon", "source", "dir")
addon_base_module = "addon" # Optional, used for absolute import check
compat.check_for_compat_issues(addon_src_dir, addon_base_module) # Check addon source code for compatibility issues
```
