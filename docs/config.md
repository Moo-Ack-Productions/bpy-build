# Config Options

> [!IMPORTANT]
> For security reasons, BpyBuild restricts the characters an action name or file
  may have. The following is allowed:
> - All English letters (a-z, A-Z)
> - Numerical digits (0-9)
> - Whitespace
> - Hyphens and underscores
> 
> BpyBuild does not count the `.py` extension for files.

- `addon_folder` (`str`): The source folder containing the addon code (`.` is not allowed)
- `build_name` (`str`): The name of the outputted build (without .zip) (***DEPRECATED, use `output_name`***)
- `output_name` (`str`): The name of the outputted build (without .zip), with templating variables
- `output_settings` (`dict`): Variable definitions for `output_name`
    - `extension` (`str`): Defined if addon is being built as an extension
    - `legacy` (`str`): Defined if addon is being built as a legacy addon
    - `windows` (`str`): Defined if addon is being built on Windows
    - `osx` (`str`): Defined if addon is being built on OSX
    - `linux` (`str`): Defined if addon is being built on Linux
    - `posix` (`str`): Defined if addon is being ran on FreeBSD, NetBSD, or OpenBSD
- `build_extension` (`bool, default `True`): Build an extension
- `extension_settings` (`dict`): Settings for extension building with the following options:
    - `build_legacy` (`bool`, default `False`): Build a legacy addon alongside an extension
        - Note: Legacy addon builds have the suffix `_legacy`
    - `remove_bl_info` (`bool, default `False): Remove `bl_info` from an addon's `__init__.py` file
        - Note: Not functional at the moment, is planned in the future.

- `build_actions` (`dict`): Actions that are mapped to some value
    - `action_name`
        - `script` (`str`): Path to the script containing the action code
        - `ignore_filters (`str`): Glob patterns of files to ignore when copying
        - `depends_on` (`list[str]`): List of actions that the current actions depends on
            - Note: These actions must be executed *before* the dependent action. Actions order is
              based on the order provided in the command line
        - `subactions` (`list[str]`): List of actions to run afterwards
            - Note: Subactions will be ran *after* the parent action
