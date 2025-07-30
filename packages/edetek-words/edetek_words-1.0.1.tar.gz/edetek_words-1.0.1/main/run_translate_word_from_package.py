# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 7/30/2025 3:53 PM
@Description: Description
@File: run_.py
"""

from src.words.core.build_map import load_data
from src.words.core.core import translate_word_from_package
from src.words.dto.translation_package import TranslationPackage

if __name__ == '__main__':
    payload = load_data("payload.json")
    p: TranslationPackage = TranslationPackage.from_dict(payload)
    translate_word_from_package(p)
