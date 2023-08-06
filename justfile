default: format mypy
  poetry build
  pipx uninstall bpy-addon-build
  pipx install $(ls -t dist/bpy_addon_build-0.1.*-py3-none-any.whl | head -1)

mypy:
  poetry run mypy --pretty bpy_addon_build

format:
  poetry run black bpy_addon_build
  just mypy

test: mypy
  poetry run bpy-addon-build -b dev -c test/bpy-build.yaml  
