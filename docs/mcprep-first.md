BpyBuild is made with an MCprep-first philosophy. This means:
- BpyBuild will gain features needed for MCprep's build system
- Backwards compatibility with MCprep's configuration is a priority

# Background
BpyBuild began as a single script called [`mcprep-build.py`](https://github.com/Moo-Ack-Productions/MCprep/blob/b31ab8a5a8bc61f6c2a07a26da0a6948dc1021fc/mcprep-build.py), to replace the annoying use of shell scripts for building MCprep (especially after the times Bash went haywire). From `mcprep-build.py` came the more general purpose BpyBuild, intended for other addons.

However from day 1 BpyBuild has always been an MCprep related project, and is bound to the needs of MCprep. 

# Tests
To verify compatibility, BpyBuild has a set of tests that use MCprep. These tests are based on the `master` branch of MCprep (unless `dev` or otherwise is needed), and are more complex compared to the regular tests. In addition, BpyBuild may also patch parts of MCprep's config to test new features, although these patches represent what we intend to use in MCprep eventually (and thus temporary).
