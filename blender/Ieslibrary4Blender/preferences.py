# Copyright (c) 2024 Jürgen Furrer
# Based on LilySurfaceScrapper
#
# This file is part of Ieslibrary4Blender, a Blender add-on to import
# ies-lights from ieslibrary.com. It is released under the terms of the MIT
# license. See the LICENSE.md file for the full text.

import bpy


# -----------------------------------------------------------------------------


def getPreferences(context=None):
    if context is None:
        context = bpy.context
    preferences = context.preferences
    addon_preferences = preferences.addons[__package__].preferences
    return addon_preferences


# -----------------------------------------------------------------------------


class Ieslibrary4BlenderPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    texture_dir: bpy.props.StringProperty(
        name="Texture Directory",
        subtype="DIR_PATH",
        default="Ieslibrary4Blender",
    )

    ieslibrary_apikey: bpy.props.StringProperty(
        name="API-Key",
        subtype="NONE",
        default="",
    )

    ies_use_strength: bpy.props.BoolProperty(
        name="Use Energy Value",
        default=True,
    )

    ies_add_blackbody: bpy.props.BoolProperty(
        name="Add Blackbody node",
        default=True,
    )

    ies_light_strength: bpy.props.BoolProperty(
        name="Use in strength node",
        default=False,
    )

    ies_pack_files: bpy.props.BoolProperty(
        name="Pack IES files internally",
        default=True,
    )

    def draw(self, context):
        layout = self.layout

        layout.label(text="The texture directory where the textures are downloaded.")
        layout.label(
            text="It can either be relative to the blend file, or global to all files."
        )
        layout.label(
            text="If it is relative, you must always save the blend file before importing lights."
        )
        layout.prop(self, "texture_dir")

        layout.label(
            text="For the import of lights from ieslibrary a valid API-Key is needed."
        )
        layout.label(text="Get the API-Key from ieslibrary.com (login needed)")
        layout.prop(self, "ieslibrary_apikey")

        layout.prop(self, "ies_add_blackbody")

        layout.prop(self, "ies_use_strength")

        if bool(self.ies_use_strength):
            layout.prop(self, "ies_light_strength")

        layout.prop(self, "ies_pack_files")


# -----------------------------------------------------------------------------

classes = (Ieslibrary4BlenderPreferences,)

register, unregister = bpy.utils.register_classes_factory(classes)
