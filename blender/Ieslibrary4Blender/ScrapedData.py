# Copyright (c) 2024 - 2024 Jürgen Furrer
# Based on LilySurfaceScrapper
#
# This file is part of Ieslibrary4Blender, a Blender add-on to import
# ies-lights from ieslibrary.com. It is released under the terms of the MIT
# license. See the LICENSE.md file for the full text.

from .settings import UNSUPPORTED_PROVIDER_ERR
from .ScrapersManager import ScrapersManager


class ScrapedData():
    """Internal representation of materials and worlds, responsible on one side for
    scrapping texture providers and on the other side to build blender materials.
    This class must not use the Blender API. Put Blender related stuff in subclasses
    like CyclesMaterialData."""

    @classmethod
    def makeScraper(cls, url):
        raise NotImplementedError

    def __init__(self, url, texture_root="", asset_name=None, scraping_type=None):
        """url: Base url to scrape
        texture_root: root directory where to store downloaded textures
        asset_name: the name of the asset / folder name
        """
        self.url = url.strip('"')
        deep_check = False
        if asset_name == "LOCAL_FILE_SCRAPER-SUBDIR":
            asset_name = None
            deep_check = True
        self.asset_name = asset_name
        self.error = None
        if url is None and asset_name is None:
            self.error = "No source given"

        self.texture_root = texture_root
        self.metadata = None
        self._scraper = type(self).makeScraper(self.url)
        self.reinstall = False

        if self._scraper is None:
            self.error = scraping_type.capitalize() + " " + UNSUPPORTED_PROVIDER_ERR
            for S in ScrapersManager.getScrapersList():
                if S.canHandleUrl(self.url) and S.scraped_type:
                    self.error = f"This URL corresponds to a {next(iter(S.scraped_type)).lower()} but you are trying to import it as a {scraping_type.lower()}"
        else:
            self._scraper.texture_root = texture_root
            self._scraper.metadata.scrape_type = scraping_type
            self._scraper.metadata.deep_check = deep_check

    def getVariantList(self):
        if self.error is not None:
            return None
        if self.metadata is not None:
            return self.metadata.variants
        if self.asset_name is not None:
            self._scraper.getVariantData(self.asset_name)
        else:
            self._scraper.fetchVariantList(self.url)
        self.metadata = self._scraper.metadata
        if not self.metadata.variants:
            self.error = self._scraper.error
        return self.metadata.variants

    def selectVariant(self, variant_index):
        if self.error is not None:
            return False
        if self.metadata is None:
            self.getVariantList()
        if not self._scraper.fetchVariant(variant_index, self):
            return False
        return True

    def setReinstall(self, value):
        self.reinstall = value
        self._scraper.reinstall = value

    def isDownloaded(self, variant):
        return self._scraper.isDownloaded(variant)
