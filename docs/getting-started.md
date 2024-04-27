# Getting Started: Building your own addoon

To get started using bpy-build to manage building and reloading your own blender addon project, follow the steps below.
Install from PyPi:
`pip install bpy-addon-build`

First create a file called `bpy-build.yaml` and add the following contents:
```yaml
addon_folder: my_addon # the folder with the addon source code
build_name: my_addon
```

> [!IMPORTANT]
> For security and compatibility reasons, BpyBuild only allows a subset of characters for `addon_folder` and `build_name`. These are:
> - All English letters (a-z, A-Z)
> - Numerical digits (0-9)
> - Whitespace
> - Hyphens and underscores

> [!CAUTION]
> Note: the addon source code must be in a subfolder! BpyBuild does not support using `.` for `addon_folder`

Then run `bab`, your addon will be built in the `build` folder!

Now let's automatically install our addon:
```yaml
addon_folder: my_addon # the folder with the addon source code
build_name: my_addon

install_versions:
  - 3.5
```

We can also do stuff during the build process. Let's add the following:
```py
# default.py
from bpy_addon_build.api import BabContext
def main(ctx: BabContext) -> None:
  print("Hello World!")
```
```yaml
during_build:
  # This will always be executed
  default:
    script: "default.py"
```

Check the [action docs](/docs/actions.md) for more information.

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
