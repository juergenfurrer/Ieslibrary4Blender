# Copyright (c) 2024 - 2024 Jürgen Furrer
# Based on LilySurfaceScrapper
#
# This file is part of Ieslibrary4Blender, a Blender add-on to import
# ies-lights from ieslibrary.com. It is released under the terms of the MIT
# license. See the LICENSE.md file for the full text.

import os

from .Scrapers.AbstractScraper import AbstractScraper

class ScrapersManager():
    all_scrapers = None

    @staticmethod
    def makeScrapersList():
        """dirty but useful, for one to painlessly write scrapping class
        and just drop them in the scrapers dir"""
        import importlib
        scrapers_names = []
        scrapers_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Scrapers")
        package = __name__[:__name__.rfind('.')]
        for f in os.listdir(scrapers_dir):
            if f.endswith(".py") and os.path.isfile(os.path.join(scrapers_dir, f)):
                scrapers_names.append(f[:-3])
        scrapers = []
        for s in scrapers_names:
            module = importlib.import_module('.Scrapers.' + s, package=package)
            for x in dir(module):
                if x == 'AbstractScraper':
                    continue
                m = getattr(module, x)
                if isinstance(m, type) and issubclass(m, AbstractScraper):
                    scrapers.append(m)
        return scrapers

    @classmethod
    def getScrapersList(cls):
        if cls.all_scrapers is None:
            cls.all_scrapers = ScrapersManager.makeScrapersList()
        return cls.all_scrapers
