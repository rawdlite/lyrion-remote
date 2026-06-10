#!/usr/bin/env python3
"""Compatibility shim for the old rotary encoder chooser module."""
from lyrionRemote.chooser_manager import create_chooser, Chooser, RotaryChooser, ButtonChooser

__all__ = ['create_chooser', 'Chooser', 'RotaryChooser', 'ButtonChooser']

# This module remains for compatibility with legacy imports.
# New code should use lyrionRemote.chooser_manager directly.
