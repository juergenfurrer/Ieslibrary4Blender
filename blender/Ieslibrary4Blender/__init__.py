# Copyright (c) 2024 - 2024 Jürgen Furrer
# Based on LilySurfaceScrapper
#
# This file is part of Ieslibrary4Blender, a Blender add-on to import
# ies-lights from ieslibrary.com. It is released under the terms of the MIT
# license. See the LICENSE.md file for the full text.

from . import preferences
from . import frontend


bl_info = {
    "name": "Ieslibrary for Blender",
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


def register():
    preferences.register()
    frontend.register()


def unregister():
    frontend.unregister()
    preferences.unregister()


if __name__ == "__main__":
    register()
