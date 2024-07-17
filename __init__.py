# Copyright (c) 2024 Jürgen Furrer
# Based on LilySurfaceScrapper
#
# This file is part of Ieslibrary4Blender, a Blender add-on to import
# ies-lights from ieslibrary.com. It is released under the terms of the MIT
# license. See the LICENSE.md file for the full text.

import os
import sys
from .blender.Ieslibrary4Blender import register

# A bit of boilerplate because this add-on is intended to be zipped with only
# the blender/Ieslibrary4Blender directory, not the root of the repo
# (preferably don't use the "Download as zip" button from GitHub, but rather
# download zip files from the release pages.

module_root = os.path.join(os.path.dirname(os.path.realpath(__file__)), "blender")
if module_root not in sys.path:
    sys.path.append(module_root)


bl_info = {
    "name": "Ieslibrary Integration",
    "author": "Jürgen Furrer <juergen@swisscode.sk>",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "Properties > Light",
    "description": "Import IES from a single URL",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "https://github.com/juergenfurrer/Ieslibrary4Blender/issues",
    "support": "COMMUNITY",
    "category": "Import",
}

if __name__ == "__main__":
    register()
