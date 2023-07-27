# Contributing Guide
Hey there, looks like you're interested in contributing to Bpy-Build! To get started, read this guide which has a lot of important information regarding contributions.

This guide will assume you already know how to use Git and understand enough Python to know how to use type annotations.

# Building Bpy-Build
To make building the final package easier, we use [Poetry](https://python-poetry.org/). To build, you can use the following command:
```sh
poetry build
```

We also use https://github.com/casey/just to make certain tasks easier. This is not required, and all of the commands used can be found in `justfile`, but it makes things a lot easier. Note that running `just` on its own will also attempt to install the final package with PipX, so you can ignore errors related to PipX not being found.

# Dynamic typing and Mypy 
The Bpy-Build project does not allow dynamic typing at all, period. The reasons are:
- Reliability: Dynamic typing is an extra source of bugs to deal with
- Cleanliness: Dynamic typing ends up looking extremely ugly

All functions must be type annotated. It is possible to add `@typing.no_type_check` above functions that need to call untyped code (which is considered dynamic by Mypy, the type checker used here) to prevent Mypy from throwing errors with untyped functions. However, instances of `@typing.no_type_check` in contributions will cause said contributions to be rejected. Thus, for contributions, we creating wrappers for untyped functions and performing casts.

We require every commit pass Mypy checks, which we utilize pre-commit hooks for (see the Pre-Commit Hooks section for more).

# Commits
All commits must use the following format:
```
50 character summary

Justification of changes with each line being 75
characters long (for reasons related to terminal 
length)
```

For a small commit, like say fixing a syntax error or typo, it may be sufficient to have just a summary, but most commits will need justification. Commits should justify the changes made, not repeat them like a parrot (that's what the 50 character summary and Git diffs are for). Failiure to follow proper commit format may prevent a contribution from being accepted into Bpy-Build, so please follow the format.

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

# Pre-Commit Hooks
Set up [pre-commit](https://pre-commit.com/). This must be installed seperately and is not included in the Poetry dependencies. Then run `pre-commit install`. This will set up pre-commit hooks for the following:
- Mypy static checking
