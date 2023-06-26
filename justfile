default: format
  poetry build
  pipx uninstall bpy-addon-build
  pipx install $(ls -t dist/bpy_addon_build-0.1.*-py3-none-any.whl | head -1)

format:
  poetry run black bpy_addon_build

test:
  poetry run bpy-addon-build -b dev test/bpy-build.yaml  
