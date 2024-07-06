# Copyright (c) 2024 - 2024 Jürgen Furrer
# Based on LilySurfaceScrapper
#
# This file is part of Ieslibrary4Blender, a Blender add-on to import
# ies-lights from ieslibrary.com. It is released under the terms of the MIT
# license. See the LICENSE.md file for the full text.


import os
import bpy

from .CyclesLightData import CyclesLightData
from .ScrapersManager import ScrapersManager
from .callback import get_callback
from .metadataHandler import Metadata
from .preferences import getPreferences
import bpy.utils.previews
from bpy.props import EnumProperty


# Operators

# I really wish there would be a cleaner way to do so: I need to prompt twice
# the user (once for the URL, then for the variant, loaded from the URL) so I
# end up with two bpy operators but they need to share custom info, not
# sharable through regular properties. SO it is shared through this global
internal_states = {}

registeredThumbnails = set()
custom_icons = bpy.utils.previews.new()

# spam prevention measure
metadataGetFailed = list()


class PopupOperator(bpy.types.Operator):
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class ObjectPopupOperator(PopupOperator):
    @classmethod
    def poll(cls, context):
        return context.active_object is not None


class CallbackProps:
    callback_handle: bpy.props.IntProperty(
        name="Callback Handle",
        description=(
            "Handle to a callback to call once the operator is done."
            + "Use Ieslibrary4Blender.register_callback(cb) to get such a handle."
        ),
        options={"HIDDEN", "SKIP_SAVE"},
        default=-1,
    )


# -------------------------------------------------------------------


class OBJECT_OT_LightScraper(PopupOperator, CallbackProps):
    """Import a light just by typing its URL. See documentation for a list of supported light providers."""

    bl_idname = "object.light_import"
    bl_label = "Import light"

    url: bpy.props.StringProperty(
        name="URL",
        description="Address from which importing the light data",
        default="",
    )

    name: bpy.props.StringProperty(
        name="Name",
        description="Get the texture using a name (for getting local files)",
        options={"HIDDEN", "SKIP_SAVE"},
        default="",
    )

    def draw(self, context):
        layout = self.layout

        layout.label(text="No valid url found in clipboard!")
        layout.label(text="Please enter a valid url into the text-field")
        layout.prop(self, "url")

    def execute(self, context):
        pref = getPreferences(context)
        if bpy.data.filepath == "" and not os.path.isabs(pref.texture_dir):
            self.report(
                {"ERROR"}, "You must save the file before using Ieslibrary4Blender"
            )
            return {"CANCELLED"}

        texdir = os.path.dirname(bpy.data.filepath)
        name = None if not self.name else self.name
        data = CyclesLightData(self.url, texture_root=texdir, asset_name=name)
        if data.error is None:
            data.getVariantList()
        if data.error is not None:
            self.report({"ERROR_INVALID_INPUT"}, data.error)
            return {"CANCELLED"}

        selected_variant = 0
        if data.selectVariant(selected_variant):
            data.createLights()
        else:
            print("scraping failed :/")
        cb = get_callback(self.callback_handle)
        cb(context)
        return {"FINISHED"}


class OBJECT_OT_ClipboardLightScraper(PopupOperator, CallbackProps):
    bl_idname = "object.light_import_from_clipboard"
    bl_label = "Import from ieslibrary.com"

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        try:
            bpy.ops.object.light_import(
                "EXEC_DEFAULT", url=bpy.context.window_manager.clipboard
            )
        except RuntimeError as err:
            msg = err.args[0]
            if msg.startswith("Invalid Input Error: "):
                # Open the input-field
                bpy.ops.object.light_import('INVOKE_DEFAULT')
            else:
                raise err
        return {"FINISHED"}


# -------------------------------------------------------------------
# Panels


class LIGHT_PT_Ieslibrary4Blender(bpy.types.Panel):
    """Panel with the IES Scraper button"""

    bl_label = "IES from ieslibrary.com"
    bl_idname = "LIGHT_PT_Ieslibrary4Blender"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == "LIGHT"

    def draw(self, context):
        layout = self.layout
        pref = getPreferences(context)
        if bpy.data.filepath == "" and not os.path.isabs(pref.texture_dir):
            layout.label(text="You must save the file to use Ieslibrary4Blender")
            layout.label(text="or setup a texture directory in preferences.")
        else:
            layout.operator("object.light_import_from_clipboard")
            urls = {None}  # avoid doubles
            for S in ScrapersManager.getScrapersList():
                if "LIGHT" in S.scraped_type and S.home_url not in urls:
                    split = False
                    factor = 1.0
                    if not hasattr(custom_icons, S.__name__) or (
                        hasattr(custom_icons, S.__name__)
                        and len(getattr(custom_icons, S.__name__)) == 0
                    ):
                        thumbnailGeneratorGenerator(S)(0, 0)
                    if len(getattr(custom_icons, S.__name__)) > 0:
                        split = True
                        factor = 0.85
                    row = layout.split(factor=factor, align=True)
                    row.operator("wm.url_open", text=S.source_name).url = S.home_url
                    if split:
                        row.template_icon_view(
                            context.scene,
                            S.__name__,
                            scale=1,
                            scale_popup=7.0,
                            show_labels=S.show_labels,
                        )
                    urls.add(S.home_url)


# Utils


def thumbnailGeneratorGenerator(scraper_cls):
    """
    TODO: It is bad design to have Blender halt for downloading metadata while drawing the UI
    """

    def generateThumbnailIcon(self, context):
        global custom_icons

        if not scraper_cls.home_dir or not scraper_cls.show_preview:
            setattr(custom_icons, scraper_cls.__name__, ())
            return ()

        items = dict()

        texdir = os.path.dirname(bpy.data.filepath)
        scraper = scraper_cls(texture_root=texdir)

        if "missingThumbnail" not in registeredThumbnails:
            registeredThumbnails.add("missingThumbnail")
            missingThumb = os.path.join(__file__, "Data", "missing_thumbnail.jpg")
            custom_icons.load("missing_thumbnail", missingThumb, "IMAGE")

        basedir = scraper.getTextureDirectory(scraper_cls.home_dir)

        # iterate over assets in scrapers home dir
        for i in os.listdir(basedir):
            # these ones dont have a metadata file, so they will be fetched using the local scraper
            if i in metadataGetFailed:
                registeredThumbnails.add(i)
                # it has a different name in case I give it a different thumbnail later, it will just default to missing
                items[i] = "local_thumbnail"  # todo check for local thumbs
                continue

            if not os.path.isdir(os.path.join(basedir, i)):
                continue
            name = f"thumb_{scraper_cls.__name__}-{i.replace(' ', '_')}"
            if i in registeredThumbnails:
                items[i] = name
                continue

            # get metadata
            metadata_file = os.path.join(basedir, i, scraper_cls.metadata_filename)
            metadata = Metadata.open(metadata_file)
            # if no metadata file was found
            if metadata.name == "":
                # try to get info
                print(f"No metadata ('{metadata_file}' not found)! getting for {i}")
                scraper.getVariantData(i)
                # if its still empty then just skip this
                if scraper.metadata.name == "":
                    print(
                        f"!! failed to get metadata for {i} from {scraper.home_url} !!"
                    )
                    metadataGetFailed.append(i)
                    continue
                metadata = scraper.metadata
            thumb_name = metadata.thumbnail

            if thumb_name is None:
                print("missing thumbnail", name)
                registeredThumbnails.add(i)
                items[i] = "missing_thumbnail"
                continue
            thumbnail = os.path.join(basedir, i, thumb_name)

            registeredThumbnails.add(i)
            custom_icons.load(name, thumbnail, "IMAGE")
            items[i] = name

        # create icons
        icons = list()
        for i, k in enumerate(items.keys()):
            icon = (
                custom_icons[items[k]].icon_id
                if items[k] in custom_icons
                else custom_icons["missing_thumbnail"].icon_id
            )
            icons.append(
                (str(k), str(k), f"{k} from {scraper_cls.source_name}", icon, i)
            )

        setattr(custom_icons, scraper_cls.__name__, tuple(icons))

        return getattr(custom_icons, scraper_cls.__name__)

    return generateThumbnailIcon


# to prevent it from spamming lights or other things with only 1 variant
running = True


def enumResponseGenerator(scraper_cls):
    def enumResult(self, context):
        global running
        if not running:
            return
        running = False

        scraper_name = scraper_cls.__name__
        asset = getattr(self, scraper_name)

        texdir = os.path.dirname(bpy.data.filepath)
        scraper = scraper_cls(texture_root=texdir)

        print(f"choose texture {scraper_cls.home_dir} / {asset}")

        basedir = scraper.getTextureDirectory(scraper_cls.home_dir)

        item_path = os.path.join(basedir, asset)

        metadata_file = os.path.join(item_path, scraper_cls.metadata_filename)
        metadata = Metadata.open(metadata_file)

        # use the local scraper
        if not metadata.name:
            metadata.fetchUrl = item_path
            metadata.name = "LOCAL_FILE_SCRAPER-SUBDIR"

        # get material
        if "LIGHT" in scraper_cls.scraped_type:
            bpy.ops.object.light_import(
                "EXEC_DEFAULT", url=metadata.fetchUrl, name=metadata.name
            )

        running = True

    return enumResult


# Registration

classes = (
    OBJECT_OT_LightScraper,
    OBJECT_OT_ClipboardLightScraper,
    LIGHT_PT_Ieslibrary4Blender,
)

rregister, unregister = bpy.utils.register_classes_factory(classes)


def register():
    global custom_icons
    rregister()
    for S in ScrapersManager.getScrapersList():
        # need to keep this list or the text breaks in menus
        setattr(custom_icons, S.__name__, ())
        setattr(
            bpy.types.Scene,
            S.__name__,
            EnumProperty(
                options={"SKIP_SAVE"},
                items=thumbnailGeneratorGenerator(S),
                update=enumResponseGenerator(S),
            ),
        )
