# Copyright (c) 2024 Jürgen Furrer
# Based on LilySurfaceScrapper
#
# This file is part of Ieslibrary4Blender, a Blender add-on to import
# ies-lights from ieslibrary.com. It is released under the terms of the MIT
# license. See the LICENSE.md file for the full text.

from .ScrapersManager import ScrapersManager
from .ScrapedData import ScrapedData


class LightData(ScrapedData):
    """Internal representation of world, responsible on one side for
    scrapping texture providers and on the other side to build blender
    materials. This class must not use the Blender API. Put Blender
    related stuff in subclasses like CyclesMaterialData."""

    def __init__(self, url, texture_root="", asset_name=None):
        super().__init__(
            url, texture_root=texture_root, asset_name=asset_name, scraping_type="LIGHT"
        )

        self.name = "IES Light"
        self.maps = {"ies": None, "energy": None}

    @classmethod
    def makeScraper(cls, url):
        for S in ScrapersManager.getScrapersList():
            if "LIGHT" in S.scraped_type and S.canHandleUrl(url):
                return S()
        return None

    def createLights(self):
        """Implement this in derived classes"""
        raise NotImplementedError
