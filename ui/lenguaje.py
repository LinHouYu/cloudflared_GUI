import os
import json
from utils import resource_path

LANG_DATA = {}
LANG_ORDER = []
CURRENT_LANG = None

# 加载所有语言文件
def load_all_languages():
    global LANG_DATA, LANG_ORDER
    LANG_DATA.clear()
    LANG_ORDER.clear()
    lang_dir = resource_path("lenguaje")
    if not os.path.isdir(lang_dir):
        raise RuntimeError("缺少 lenguaje 文件夹")
    for fname in sorted(os.listdir(lang_dir)):
        if fname.endswith(".json"):
            key = os.path.splitext(fname)[0]  # 文件名作为语言 key
            with open(os.path.join(lang_dir, fname), "r", encoding="utf-8") as f:
                LANG_DATA[key] = json.load(f)
                LANG_ORDER.append(key)
    if not LANG_ORDER:
        raise RuntimeError("没有语言文件")

# 设置当前语言
def set_language(lang_key: str):
    global CURRENT_LANG
    if lang_key not in LANG_DATA:
        raise ValueError(f"语言 {lang_key} 不存在")
    CURRENT_LANG = lang_key

# 获取当前语言包
def get_pack():
    if CURRENT_LANG is None:
        raise RuntimeError("未设置当前语言")
    return LANG_DATA[CURRENT_LANG]
