# Contributing Guide
Hey there, looks like you're interested in contributing to Bpy-Build! To get started, read this guide which has a lot of important information regarding contributions.

> [!CAUTION]
> For those that have contributed to MCprep in the past, note that BpyBuild has stricter contributing requirements in comparison.

This guide will assume you already know how to use Git and understand enough Python to know how to use type annotations.

# Building Bpy-Build
To make building the final package easier, we use [Poetry](https://python-poetry.org/). To build, you can use the following command:
```sh
poetry install
poetry build
```

We also use https://github.com/casey/just to make certain tasks easier. This is not required, and all of the commands used can be found in `justfile`, but it makes things a lot easier. Note that running `just` on its own will also attempt to install the final package with PipX, so you can ignore errors related to PipX not being found.

# Dynamic typing and Mypy 
The Bpy-Build project does not allow dynamic typing at all, period. The reasons are:
- Reliability: Dynamic typing is an extra source of bugs to deal with
- Cleanliness: Dynamic typing ends up looking extremely ugly

All functions must be type annotated. Instances of `@typing.no_type_check` or `# type: ignore` that aren't justified with a comment will cause said contributions to be rejected. Thus, for contributions, we creating wrappers for untyped functions and performing casts.

We require every commit pass Mypy checks, which we utilize pre-commit hooks for (see the Pre-Commit Hooks section for more). Alternatively, you can use the following:
```sh
just mypy

# Or if you don't have just installed
poetry run mypy --pretty bpy_addon_build
```

All commits will be checked for passing tests, and PRs will be rejected if one does not pass the Mypy checks.

## Typing
Although BpyBuild supports Python 3.8, we try to use [PEP 585](https://peps.python.org/pep-0585/) types wherever possible, using `annotations` from the `__futures__` module. This means for the most part, `dict`, `list`, `tuple`, etc. can be used with little issue. That being said, the following has to be kept in mind:
- These annotations are hackish in the CPython interpreter, so these can't be used for `attrs`/`cattrs` classes, or if `cast` needs to be performed. In those cases, their `typing` counterparts will have to be used
- New files that use PEP 585 annotations will need to have `from __future__ import annotations` as the first import in the file
- Although it would be nice, [PEP 604](https://peps.python.org/pep-0604/) syntax for Unions is not an option with `__futures__` in Python 3.8

Despite some of the headaches with using annotations from `__futures__`, we encourage their use so that migrating becomes less of a burden in the future.

# Formatting
All commits must be formatted with https://github.com/astral-sh/ruff. We have a pre-commit hook for this (see the Pre-Commit Hooks section).

In addition, Ruff is a developer dependency defined in `pyproject.toml`, in case you want to run it at any moment in time, which can be done with the following:
```sh
just format

# Or if you don't have just installed
poetry run ruff format bpy_addon_build
```

# Commits
All commits must use the following format:
```
50 character summary

Justification of changes with each line being 75
characters long (for reasons related to terminal 
length)
```

In addition, the 50 character summary at the top must follow the [Conventional Commit Format](https://www.conventionalcommits.org/en/v1.0.0/).

Commits that fall under the following **ARE REQUIRED** to give justification:
- `feat`
- `refactor`

That being said, it's best to give justification for every commit.

To make meeting this requirement easier, one can make a `.gitmessage` file somewhere with the following :
```
# Title: Summary, imperative, start upper case, don't end with a period
# One line only
# No more than 50 chars. #### 50 chars is here:  #


# One line of space to split summary and justification ^
# Body: Explain *what* and *why* (not *how*).
# Wrap at 72 chars. ################################## which is here:  #

```

And run the following:
```sh
git config --local commit.template /path/to/.gitmessage
git config --local commit.verbose true
```

This will make all commits use that template and perform verbose commits (where commits are opened as their own file, with saving and closing creating the commit itself).

## Commits MUST *fully commit* to a given change
When a commit is made, the change stated in the commit must be fully committed to. For example, a commit that states `refactor: Use sys.exit method for program exit` **must** implement that change across all files, not just one or two.

# Pre-Commit Hooks
To make things easier for developers, we define pre-commit hooks that allow developers to commit changes and automatically have Mypy and Black run on said commit. This is not required
Set up [pre-commit](https://pre-commit.com/). This must be installed separately and is not included in the Poetry dependencies. Then run `pre-commit install`. This will set up pre-commit hooks for the following:
- Mypy static checking
- Linting with Ruff
- Code formatting with Ruff

# Tests
BpyBuild has 2 sets of unittests, `test/tests.py` and `test/mcprep_tests.py`. The former tests every feature in BpyBuild, but isn't sophisticated. The latter clones the MCprep repo, which means less features are used, but the tests are more sophisticated and test for backwards compatibility (as required under [MCprep-first development](/docs/mcprep-first.md)).

To run with Poetry, the following commands can be used:
- Regular tests: `poetry run python -m unittest test.tests`
- MCprep tests: `poetry run python -m unittest test.mcprep_tests`
