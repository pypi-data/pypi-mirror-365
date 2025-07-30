# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////
# EzQt_App - A Modern Qt Application Framework
# ///////////////////////////////////////////////////////////////
#
# Author: EzQt_App Team
# Website: https://github.com/ezqt-app/ezqt_app
#
# This file is part of EzQt_App.
#
# EzQt_App is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# EzQt_App is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with EzQt_App.  If not, see <https://www.gnu.org/licenses/>.
# ///////////////////////////////////////////////////////////////

# IMPORT BASE
# ///////////////////////////////////////////////////////////////

# IMPORT SPECS
# ///////////////////////////////////////////////////////////////

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////

# TYPE HINTS IMPROVEMENTS
from typing import Dict

# UTILITY FUNCTIONS
# ///////////////////////////////////////////////////////////////

# CLASS
# ///////////////////////////////////////////////////////////////

# SUPPORTED LANGUAGES
# ///////////////////////////////////////////////////////////////

# Supported languages
SUPPORTED_LANGUAGES: Dict[str, Dict[str, str]] = {
    "en": {"name": "English", "native_name": "English", "file": "ezqt_app_en.ts"},
    "fr": {"name": "Français", "native_name": "Français", "file": "ezqt_app_fr.ts"},
    "es": {"name": "Español", "native_name": "Español", "file": "ezqt_app_es.ts"},
    "de": {"name": "Deutsch", "native_name": "Deutsch", "file": "ezqt_app_de.ts"},
}

# DEFAULT SETTINGS
# ///////////////////////////////////////////////////////////////

# Default language
DEFAULT_LANGUAGE: str = "en"

# Translations directory
TRANSLATIONS_DIR: str = "resources/translations"
