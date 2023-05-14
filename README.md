# Bpy-build
A tool to make building addons faster

# How to use
First create a file called `bpy-build.yaml` and add the following contents:
```yaml
addon_folder: . # or the folder with the addon source code
build_name: my_addon
```

Then run `bpy-addon-build`, your addon will be built in the `build` folder!

Now let's automatically install our addon:
```yaml
addon_folder: . # or the folder with the addon source code
build_name: my_addon

install_versions:
  - '3.5'
```

Our addon will now automatically be installed in Blender 3.5! If it doesn't exist, `bpy-build` will just ignore it.

