# Output Names

Starting with 0.6, BpyBuild allows defining build names using variables,
which can be used to handle naming across multiple configurations. For example,
if an addon has compiled components, BpyBuild can use templates to automatically
fill in the OS information.

## Built-in Static Variables

Built-in static variables are reserved names that can be defined in the `output_settings`
portion of the BpyBuild config. They are:

- `extension` (`str`): Defined if addon is being built as an extension
- `legacy` (`str`): Defined if addon is being built as a legacy addon
- `windows` (`str`): Defined if addon is being built on Windows
- `osx` (`str`): Defined if addon is being built on OSX
- `linux` (`str`): Defined if addon is being built on Linux
- `posix` (`str`): Defined if addon is being ran on FreeBSD, NetBSD, or OpenBSD

They can easily be used as follows:

```yaml

output_name: Addon_{windows|osx|linux|''}_{extension|legacy}

output_settings:
  extension: extension_build
  legacy: legacy_build
  windows: windows
  osx: macos
  linux: linux
```

Each variable is assigned to a value, and is used in braces. We'll call the part
in braces *expressions*. In these expressions, the `|` operator is also used, which
simply defines fallback behavior. So for example, the expression:

```
windows | osx | linux | ''
```

Translates into:

- Use `windows` if defined, otherwise
  - Use `osx` if defined, otherwise
    - Use `linux` if defined, otherwise
      - use the string `''`

The last `''` is important, because it's a constant, and as such will always be a
defined expression. If instead we had:

```
windows | osx | linux
```

And all 3 variables were undefined, then the entire expression is undefined, and
BpyBuild will throw an error. For built-in static variables, that's simply a matter
of adding them into the config file, but with dynamic variables, debugging an issue
with definitions may be difficult.

## Built-in Dynamic Variables

Unlike static variables, these are always defined regardless, since they're defined
using built-in actions and the `dynamic_name` hook. They are:

- `version` (`str`): Extracted version of the addon, in the form X.Y.Z

# Dynamic Action-defined Variables

There's 2 parts to creating action-defined variables: first, they must
be declared in `output_settings` with the `@dynamic` or
`@dynamic_required` keywords, as follows:

```yaml
output_settings:
  dynamic_var: '@dynamic'
  dynamic_var_2: '@dynamic_required'
```

The `@dynamic` keyword signifies that a variable is dynamically defined in an
action. However, it should be noted that the variable is not guaranteed to be
defined, so fallbacks *should* be used.

> [!IMPORTANT]
> Officially, dynamic variables defined as just `@dynamic` are required to have
  fallbacks. While not enforced in BpyBuild 0.6, it will be at some point in the
  future, so it's advised to use them as if fallbacks were enforced, because
  eventually, they will be.

Alternatively, the `@dynamic_required` keyword can be used, in which BpyBuild
enforces the existence of a dynamic variable after all `dynamic_name` hooks are ran.
If a variable defined as `@dynamic_required` is not defined after all `dynamic_name`
hooks are ran, than BpyBuild will throw an error.

Once defined as dynamic in the config, a `dynamic_name` hook is needed in an action.
This is ran after all `pre_build` hooks, in the same directory, but unlike `pre_build`
hooks, must return a list of all newly defined variables.

For example, to create a dynamic variable named `foo`, with the value `bar`:

```yaml
output_name: Addon_{foo}

output_settings:
  foo: '@dynamic_required'
```

```py
from bpy_addon_build.api import BabContext, BpyError, BpyVariableDef

def dynamic_name(ctx: BabContext) -> list[BpyVariableDef]:
    return BpyVariableDef("foo", "bar")
```
