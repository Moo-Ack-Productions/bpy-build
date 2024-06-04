# BpyBuild Actions

One feature of BpyBuild is the ability to write scripts and run them at build time. This page goes over how to write a build script.

# Quick Start
Here's an example of a simple action:
```yaml
# bpy-build.yaml
build_actions:
  dev: 
    script: "dev.py"
```

```py
# dev.py
from bpy_addon_build.api import BabContext

def main(ctx: BabContext) -> None:
    print("DEV MAIN")
    with open((ctx.current_path / "mcprep_dev.txt"), "w") as f:
        f.write("hi guys c:")
```

> [!CAUTION]
> **Never** put action related code in the global scope. 
>
> BpyBuild doesn't run scripts in the traditional sense. Instead, BpyBuild imports scripts as Python modules and runs `main`. As such, global code is executed on import, which is before the actual build process.

> [!IMPORTANT]
> For security reasons, BpyBuild restricts the characters an action name or file may have. The following is allowed:
> - All English letters (a-z, A-Z)
> - Numerical digits (0-9)
> - Whitespace
> - Hyphens and underscores
> 
> BpyBuild does not count the `.py` extension for files.

# Hooks
BpyBuild also supports the concept of hooks. Currently, the following hooks are supported:
- `main`: executed during the build process; directory is set to a copy of the source tree under `build/stage-1`
- `pre_build`: executed before building; directory is set to the `addon_folder` variable defined in `bpy-build.yaml`
- `pre_install`: executed before installing the built addon; directory is set to `build/`
- `post_install`: executed after installing the built addon; directory is set to the addons folder of the Blender version last installed to
- `clean_up`: executed after all other build processes; directory is set to the `addon_folder` variable defined in `bpy-build.yaml`

> [!IMPORTANT]
> `pre_install` and `post_install` are executed for each version BpyBuild installs the addon to. For example, if BpyBuild installs to Blender 4.0 and Blender 4.1, `pre_install` and `post_install` will be executed twice, once for 4.0 and once for 4.1

To use one of these hooks, simply define an action using the name:
```py
# dev.py
from bpy_addon_build.api import BabContext

def clean_up(ctx: BabContext):
    # do stuff...
```

## Returning warnings and error
What if you want to raise an error or warning at build time? Well that's easy with `BpyError` and `BpyWarning`. These are simple to use:
```py
# dev.py

from bpy_addon_build.api import BabContext, BpyWarning, BpyError

def main(ctx: BabContext):
    return BpyWarning("Warning, but continue on")

def clean_up(ctx: BabContext):
    return BpyError("Error in cleanup!")
```

> [!IMPORTANT]
> An empty return statement (i.e. `return` with no value) is interpreted as success

# Using `BabContext`
`BabContext` is a required argument for all functions in BpyBuild. It's a simple dataclass defined as follows:
```py
@dataclass
class BabContext:
    # Target path of the 
    # action
    current_path: Path
```

- `current_path`: the path of the action's target directory. This can be thought of as the working directory for the action, though the working directory is not changed when running actions.

# Compatibility 
> [!CAUTION]
> This is intended for MCprep through [MCprep-first development](/docs/mcprep-first.md)

For backwards compatibility, BpyBuild can run declarations of the `main` hook with no arguments, at the cost of not being allowed to return warnings or errors. If argument-less `main` exists, it will be ran with the working directory set to the build directory.

For example:
```py
def main() -> None:
    # do stuff...
```

