# Copyright (c) 2024 Jürgen Furrer
# Based on LilySurfaceScrapper
#
# This file is part of Ieslibrary4Blender, a Blender add-on to import
# ies-lights from ieslibrary.com. It is released under the terms of the MIT
# license. See the LICENSE.md file for the full text.

import random

"""
This module is used to register callbacks that operators will call once they are done.
It works around a bpy API issue which is that it makes very hard to wait for an
operator to finish. It converts callbacks into numeric handles that can be provided
through operator properties.
"""

callback_dict = {}


def register_callback(callback):
    """
    @param callback: a function to call after.an operator is done,
    taking a unique argument which is the context
    @return: a handle to the callback, to be provided to the operator
    """
    limit = 1677216
    if len(callback_dict) > limit / 4:
        print("Too many callback registered")
        return -1
    handle = random.randint(0, limit)
    while handle in callback_dict:
        handle = random.randint(0, limit)
    callback_dict[handle] = callback
    return handle


def get_callback(handle):
    return callback_dict.get(handle, lambda context: None)
