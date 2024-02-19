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
def main() -> None:
    with open("mcprep_dev.txt", "w") as f:
        f.write("hi guys c:")

# Not required, but useful for testing
if __name__ == "__main__":
    main()
```

> [!CAUTION]
> **Never** put action related code in the global scope. 
>
> BpyBuild doesn't run scripts in the traditional sense. Instead, BpyBuild imports scripts as Python modules and runs `main`. As such, global code is executed on import, which is before the actual build process.

# Hooks
BpyBuild also supports the concept of hooks. Currently, the following hooks are supported:
- `main`: executed during the build process; working directory is set to a copy of the source tree under `build/stage-1`
- `pre_build`: executed before building; working directory is set to the `addon_folder` variable defined in `bpy-build.yaml`
- `pre_install`: executed before installing the built addon; working directory is set to `build/`
- `post_install`: executed after installing the built addon; working directory is set to the addons folder of the Blender version last installed to
- `clean_up`: executed after all other build processes; working directory is set to the `addon_folder` variable defined in `bpy-build.yaml`

> [!IMPORTANT]
> `pre_install` and `post_install` are executed for each version BpyBuild installs the addon to. For example, if BpyBuild installs to Blender 4.0 and Blender 4.1, `pre_install` and `post_install` will be executed twice, once for 4.0 and once for 4.1

To use one of these hooks, simply define an action using the name:
```py
# dev.py
def clean_up():
    # do stuff...
```

## Returning warnings and error
What if you want to raise an error or warning at build time? Well that's easy with `BpyError` and `BpyWarning`. These are simple to use:
```py
# dev.py

from bpy_addon_build.api import BpyError

def main():
    return BpyWarning("Warning, but continue on")

def clean_up():
    return BpyError("Error in cleanup!")
```

> [!IMPORTANT]
> An empty return statement (i.e. `return` with no value) is interpreted as success