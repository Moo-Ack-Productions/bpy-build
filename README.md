# Bpy-build
A tool to make building addons faster

# How to use
Install from PyPi:
`pip install bpy-addon-build`

First create a file called `bpy-build.yaml` and add the following contents:
```yaml
addon_folder: my_addon # the folder with the addon source code
build_name: my_addon
```

**Note: the addon source code must be in a subfolder! BpyBuild does not support using `.` for `addon_folder`**

Then run `bab`, your addon will be built in the `build` folder!

Now let's automatically install our addon:
```yaml
addon_folder: my_addon # the folder with the addon source code
build_name: my_addon

install_versions:
  - 3.5
```

We can also do stuff during the build process:
```yaml
during_build:
  # This will always be executed
  default:
    script: "default.py"
```

When we build, the default case will always run. We can also define cases we want to only run if we specify them:
```yaml
during_build:
  # This will always be executed
  default:
    script: "default.py"
  dev:
    script: "dev.py"
    
    # We can ignore files as 
    # well if we want to speed
    # up build times for dev builds
    ignore_filters:
      - "*.blend"
```

To run the `dev` case, we pass the `-b` argument, like `bpy-addon-build -b dev`. Note that when making an action, the action is ran at the root of your addon folder.

Our addon will now automatically be installed in Blender 3.5! If it doesn't exist, `bpy-build` will just ignore it.

```
BSD 3-Clause License

Copyright (c) 2024, Mahid Sheikh

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```
