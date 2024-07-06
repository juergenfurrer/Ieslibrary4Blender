# Copyright (c) 2024 - 2024 Jürgen Furrer
# Based on LilySurfaceScrapper
#
# This file is part of Ieslibrary4Blender, a Blender add-on to import
# ies-lights from ieslibrary.com. It is released under the terms of the MIT
# license. See the LICENSE.md file for the full text.

import bpy
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


# Define "Extras" menu
def menu_func(self, context):
    layout = self.layout
    layout.operator_context = "INVOKE_REGION_WIN"

    layout.operator(
        "object.light_import_from_clipboard",
        text="IES from ieslibrary.com",
        icon="OUTLINER_DATA_LIGHT",
    )


classes = []


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    preferences.register()
    frontend.register()

    # Add "Extras" menu to the "Add Light" menu and context menu.
    bpy.types.VIEW3D_MT_light_add.append(menu_func)


def unregister():
    frontend.unregister()
    preferences.unregister()

    # Remove "Extras" menu from the "Add Light" menu and context menu.
    bpy.types.VIEW3D_MT_light_add.remove(menu_func)

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
