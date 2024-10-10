default: format mypy
  poetry build
  pipx uninstall bpy-addon-build
  pipx install $(ls -t dist/bpy_addon_build-*-py3-none-any.whl | head -1)

mypy:
  poetry run mypy --pretty bpy_addon_build

format:
  poetry run ruff format bpy_addon_build

test:
  poetry run bab -b dev -c test/bpy-build.yaml  
