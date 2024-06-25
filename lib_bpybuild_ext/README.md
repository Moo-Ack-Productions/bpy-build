# LibBpyBuildExt

LibBpyBuildExt is a BSD 3-Clause reimplementation of the Blender Extension builder, with the goal of creating an implementation of the Blender Extension builder under a more permissive license, and as a library. This exists because the Blender Extension builder, while open source, is under the GPL. Since BpyBuild is under the BSD 3-Clause license, a permissive reimplementation is necessary.

Although the goal initially was to have 100% feature parity with the Blender Extension builder, we've since decided that full feature parity [is impractical](https://github.com/Moo-Ack-Productions/bpy-build/issues/18#issuecomment-2186680088). Thus, LibBpyBuildExt will only implement what the Blender Manual for extensions mentions.