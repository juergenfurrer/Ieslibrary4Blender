# Copyright (c) 2024 Jürgen Furrer
# Based on LilySurfaceScrapper
#
# This file is part of Ieslibrary4Blender, a Blender add-on to import
# ies-lights from ieslibrary.com. It is released under the terms of the MIT
# license. See the LICENSE.md file for the full text.

import bpy

from .LightData import LightData
from .cycles_utils import autoAlignNodes
from .preferences import getPreferences
import os


class CyclesLightData(LightData):
    def createLights(self):
        pref = getPreferences()

        selected_item = None
        selected_items = bpy.context.selected_objects
        if selected_items is not None and len(selected_items) > 0:
            # Use the first selected object
            selected_item = selected_items[0]

        if selected_item is None:
            # in case there is no selected object, try to use the active object
            selected_item = bpy.context.active_object

        if selected_item is not None and (
            selected_item.type == "POINT" or selected_item.type == "LIGHT"
        ):
            light_data = bpy.data.lights.new(self.name, "POINT")
            bpy.context.object.data = light_data
        else:
            light_data = bpy.data.lights.new(self.name, "POINT")
            light_object = bpy.data.objects.new(name=self.name, object_data=light_data)

            # Set the light to 3D cursor
            light_object.location = bpy.context.scene.cursor.location

            # Add links
            bpy.context.collection.objects.link(light_object)
            # bpy.context.view_layer.objects.active = light_object

        light_data.use_nodes = True
        light_data.shadow_soft_size = 0

        tree = light_data.node_tree
        nodes = tree.nodes
        links = tree.links

        nodes.clear()

        ies = self.maps["ies"]
        energy = self.maps["energy"]

        out = nodes.new(type="ShaderNodeOutputLight")
        emission = nodes.new(type="ShaderNodeEmission")

        links.new(out.inputs["Surface"], emission.outputs["Emission"])

        iesNode = nodes.new(type="ShaderNodeTexIES")
        if pref.ies_pack_files:
            bpy.ops.text.open(filepath=ies, internal=False)
            iesNode.ies = bpy.data.texts[os.path.basename(ies)]
        else:
            iesNode.mode = "EXTERNAL"
            iesNode.filepath = ies
        links.new(iesNode.outputs["Fac"], emission.inputs["Strength"])

        if pref.ies_use_strength:
            if pref.ies_light_strength:
                value = nodes.new(type="ShaderNodeValue")
                value.outputs["Value"].default_value = energy
                links.new(value.outputs["Value"], iesNode.inputs["Strength"])
            else:
                light_data.energy = energy

        if pref.ies_add_blackbody:
            blacbody = nodes.new(type="ShaderNodeBlackbody")
            blacbody.inputs["Temperature"].default_value = 7000
            links.new(blacbody.outputs["Color"], emission.inputs["Color"])

        autoAlignNodes(out)

        return light_data
