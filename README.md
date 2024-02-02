# Bpy-build
A tool to make building addons faster

# How to use
Install from PyPi:
`pip install bpy-addon-build`

First create a file called `bpy-build.yaml` and add the following contents:
```yaml
addon_folder: . # or the folder with the addon source code
build_name: my_addon
```

Then run `bab`, your addon will be built in the `build` folder!

Now let's automatically install our addon:
```yaml
addon_folder: . # or the folder with the addon source code
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

